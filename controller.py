from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, ipv4, udp


class Project7Controller(app_manager.OSKenApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Project7Controller, self).__init__(*args, **kwargs)

        self.mac_to_port = {}
        self.udp_packet_count = {}

        self.logger.info("Project 7 SDN Controller Started")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                datapath.ofproto.OFPP_CONTROLLER,
                datapath.ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

        self.logger.info("Switch connected: %s", datapath.id)

    def add_flow(self, datapath, priority, match, actions):

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS, actions
            )
        ]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions
        )

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        in_port = msg.match["in_port"]

        parsed_packet = packet.Packet(msg.data)

        eth = parsed_packet.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        if eth.ethertype == 0x88cc:
            return

        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][eth.src] = in_port

        out_port = self.mac_to_port[dpid].get(
            eth.dst, ofproto.OFPP_FLOOD
        )

        actions = [parser.OFPActionOutput(out_port)]

        ip_pkt = parsed_packet.get_protocol(ipv4.ipv4)
        udp_pkt = parsed_packet.get_protocol(udp.udp)

        is_project_udp = (
            ip_pkt is not None
            and udp_pkt is not None
            and udp_pkt.dst_port == 5000
        )

        if is_project_udp and out_port != ofproto.OFPP_FLOOD:

            key = (dpid, ip_pkt.src, ip_pkt.dst)

            self.udp_packet_count[key] = (
                self.udp_packet_count.get(key, 0) + 1
            )

            count = self.udp_packet_count[key]

            self.logger.info(
                "UDP monitoring: %s packets observed",
                count
            )

            if count == 5:

                match = parser.OFPMatch(
                    in_port=in_port,
                    eth_type=0x0800,
                    ip_proto=17,
                    ipv4_src=ip_pkt.src,
                    ipv4_dst=ip_pkt.dst,
                    udp_dst=5000
                )

                self.add_flow(
                    datapath,
                    10,
                    match,
                    actions
                )

                self.logger.info(
                    "Dynamic UDP forwarding rule installed"
                )

        elif out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=eth.src,
                eth_dst=eth.dst
            )

            self.add_flow(datapath, 1, match, actions)

        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )

        datapath.send_msg(out)

