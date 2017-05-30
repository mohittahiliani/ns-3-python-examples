# -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2010 IITP RAS
#  * Copyright (c) 2016 NITK Surathkal
#  *
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation;
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  *
#  * Authors: Pavel Boyko <boyko@iitp.ru>
#  * Ported to Python by: Shrishti <shrishtiak26894@gmail.com>
#  *                      Kavya Sree Bhagavatula <kavyasbhagavatula@gmail.com>
#  */

#
# Classical hidden terminal problem and its RTS/CTS solution.
#
# Topology: [node 0] <-- -50 dB --> [node 1] <-- -50 dB --> [node 2]
#
# This example illustrates the use of
#  - Wifi in ad-hoc mode
#  - Matrix propagation loss model
#  - Use of OnOffApplication to generate CBR stream
#  - IP flow monitor
#

import ns.core
import ns.propagation
import ns.applications
import ns.mobility
import ns.internet
import ns.flow_monitor
import ns.wifi

# Run single 10 seconds experiment with enabled or disabled RTS/CTS mechanism
def experiment(enableCtsRts):

    # 0. Enable or disable CTS/RTS
    ctsThr = 100 if enableCtsRts else 2200
    ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.UintegerValue (ctsThr))

    # 1. Create 3 nodes
    nodes = ns.network.NodeContainer ()
    nodes.Create (3)

    # 2. Place nodes somehow, this is required by every wireless simulation
    i = 0
    while i < 3:
        nodes.Get (i).AggregateObject (ns.mobility.ConstantPositionMobilityModel ())
        i += 1

    # 3. Create propagation loss matrix
    lossModel = ns.propagation.MatrixPropagationLossModel ()
    lossModel.SetDefaultLoss (200) #set default loss to 200 dB (no link)
    lossModel.SetLoss (nodes.Get (0).GetObject (ns.mobility.MobilityModel.GetTypeId ()), nodes.Get (1).GetObject (ns.mobility.MobilityModel.GetTypeId ()), 50)
    lossModel.SetLoss (nodes.Get (2).GetObject (ns.mobility.MobilityModel.GetTypeId ()), nodes.Get (1).GetObject (ns.mobility.MobilityModel.GetTypeId ()), 50)

    # 4. Create & setup wifi channel
    wifiChannel = ns.wifi.YansWifiChannel ()
    wifiChannel.SetPropagationLossModel (lossModel)
    wifiChannel.SetPropagationDelayModel (ns.propagation.ConstantSpeedPropagationDelayModel ())

    # 5. Install wireless devices
    wifi = ns.wifi.WifiHelper ()
    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211b)
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
                                  "DataMode", ns.core.StringValue ("DsssRate2Mbps"),
                                  "ControlMode", ns.core.StringValue ("DsssRate1Mbps"))

    wifiPhy = ns.wifi.YansWifiPhyHelper.Default ()
    wifiPhy.SetChannel (wifiChannel)
    wifiMac = ns.wifi.NqosWifiMacHelper.Default ()
    wifiMac.SetType ("ns3::AdhocWifiMac")  # use ad-hoc MAC
    devices = wifi.Install (wifiPhy,wifiMac,nodes)

    # uncomment the following to have athstats output
    # athstats=ns3.AthstatsHelper ()
    # athstats.EnableAthstats ("rtscts-athstats-node-py" if enableCtsRts else "basic-athstats-node-py", nodes)

    # uncomment the following to have pcap output
    # wifiPhy.EnablePcap ("rtscts-pcap-node-py" if enableCtsRts else "basic-pcap-node-py",nodes)

    # 6. Install TCP/IP stack & assign IP addresses
    internet = ns.internet.InternetStackHelper ()
    internet.Install (nodes)
    ipv4 = ns.internet.Ipv4AddressHelper ()
    ipv4.SetBase (ns.network.Ipv4Address ("10.0.0.0"), ns.network.Ipv4Mask ("255.0.0.0"))
    ipv4.Assign (devices)

    # 7. Install applications: two CBR streams each saturating the channel
    cbrApps = ns.network.ApplicationContainer ()
    cbrPort = 12345
    onOffHelper = ns.applications.OnOffHelper ("ns3::UdpSocketFactory", ns.network.InetSocketAddress (ns.network.Ipv4Address ("10.0.0.2"), cbrPort))
    onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (1400))
    onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
    onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))

    # flow 1:  node 0 -> node 1
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("3000000bps"))
    onOffHelper.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (1.000000)))
    cbrApps.Add (onOffHelper.Install (nodes.Get (0)))

    # flow 2:  node 2 -> node 1
    # \internal
    # The slightly different start times and data rates are a workaround
    # for \bugid{388} and \bugid{912}
    #
    onOffHelper.SetAttribute ("DataRate", ns.core.StringValue ("3001100bps"))
    onOffHelper.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (1.001)))
    cbrApps.Add (onOffHelper.Install (nodes.Get (2)))

    # \internal
    # We also use separate UDP applications that will send a single
    # packet before the CBR flows start. 
    # This is a workaround for the lack of perfect ARP, see \bugid{187}
    #
    echoPort = 9
    echoClientHelper = ns.applications.UdpEchoClientHelper (ns.network.Ipv4Address ("10.0.0.2"), echoPort)
    echoClientHelper.SetAttribute ("MaxPackets", ns.core.UintegerValue (1))
    echoClientHelper.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Seconds (0.1)))
    echoClientHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (10))
    pingApps = ns.network.ApplicationContainer ()

    # again using different start times to workaround Bug 388 and Bug 912
    echoClientHelper.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (0.001)))
    pingApps.Add (echoClientHelper.Install(nodes.Get (0)))
    echoClientHelper.SetAttribute ("StartTime", ns.core.TimeValue (ns.core.Seconds (0.006)))
    pingApps.Add (echoClientHelper.Install (nodes.Get (2)))

    # 8. Install FlowMonitor on all nodes
    flowmon = ns.flow_monitor.FlowMonitorHelper ()
    monitor = flowmon.InstallAll ()

    # 9. Run simulation for 10 seconds
    ns.core.Simulator.Stop (ns.core.Seconds (10))
    ns.core.Simulator.Run ()

    # 10. Print per flow statistics
    monitor.CheckForLostPackets ()
    classifier = ns.flow_monitor.Ipv4FlowClassifier ()
    classifier = flowmon.GetClassifier ()
    stats = monitor.GetFlowStats ()
    for flow_id, flow_stats in monitor.GetFlowStats ():
        # first 2 FlowIds are for ECHO apps, we don't want to display them

        # Duration for throughput measurement is 9.0 seconds, since
        # StartTime of the OnOffApplication is at about "second 1"
        # and
        # Simulator::Stops at "second 10".
        t = classifier.FindFlow(flow_id)
        if flow_id > 2:
            print "FlowID %i (%s -> %s)" % \
            (flow_id-2, t.sourceAddress, t.destinationAddress)
            print >> sys.stdout, "  Tx Packets: ", flow_stats.txPackets
            print >> sys.stdout, "  Tx Bytes: ", flow_stats.txBytes
            print >> sys.stdout, "  TxOffered:  ", flow_stats.txBytes * 8.0 / 9.0 / 1000 / 1000  , " Mbps"
            print >> sys.stdout, "  Rx Packets: ", flow_stats.rxPackets
            print >> sys.stdout, "  Rx Bytes: ", flow_stats.rxBytes
            print >> sys.stdout, "  Throughput: ", flow_stats.rxBytes * 8.0 / 9.0 / 1000 / 1000  , " Mbps"

    # 11. Cleanup
    ns.core.Simulator.Destroy ()

def main(argv):
    print "Hidden station experiment with RTS/CTS disabled:"
    experiment (0)
    print "------------------------------------------------"
    print "Hidden station experiment with RTS/CTS enabled:"
    experiment (1)

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))
