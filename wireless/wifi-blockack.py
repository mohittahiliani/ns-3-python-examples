# -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2009 MIRKO BANCHI
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
#  * Author: Mirko Banchi <mk.banchi@gmail.com>
#  * Ported to Python by: Shrishti <shrishtiak26894@gmail.com>
#  *                      Kavya Sree Bhagavatula <kavyasbhagavatula@gmail.com>
#  */

#
# This is a simple example in order to show how 802.11e compressed block ack mechanism could be used.
#
# Network topology:
# 
#  Wifi 192.168.1.0
# 
#        AP
#   *    *
#   |    |
#   n1   n2 
#
# In this example a QoS sta sends UDP datagram packets to access point. On the access point
# there is no application installed so it replies to every packet with an ICMP frame. However
# our attention is on originator sta n1. We have set blockAckThreshold (mininum number of packets to use
# block ack) to 2 so if there are in the BestEffort queue more than 2 packets a block ack will be
# negotiated. We also set a timeout for block ack inactivity to 3 blocks of 1024 microseconds. This timer is
# reset when:
#    - the originator receives a block ack frame.
#    - the recipient receives a block ack request or a MPDU with ack policy Block Ack. 
#

import ns.core
import ns.internet
import ns.network
import ns.applications
import ns.wifi
import ns.mobility

def main(argv):
    ns.core.LogComponentEnable ("EdcaTxopN", ns.core.LOG_LEVEL_DEBUG)
    ns.core.LogComponentEnable ("BlockAckManager", ns.core.LOG_LEVEL_INFO)

    sta = ns.network.Node ()
    ap = ns.network.Node ()

    channel = ns.wifi.YansWifiChannelHelper.Default ()
    phy = ns.wifi.YansWifiPhyHelper.Default ()
    phy.SetChannel (channel.Create ())

    wifi = ns.wifi.WifiHelper.Default ()
    mac = ns.wifi.QosWifiMacHelper.Default ()
    # disable fragmentation
    wifi.SetRemoteStationManager ("ns3::AarfWifiManager", "FragmentationThreshold", ns.core.UintegerValue (2500))
    
    ssid = ns.wifi.Ssid ("My-network")
    
    mac.SetType ("ns3::StaWifiMac",
                 "QosSupported", ns.core.BooleanValue (True),
                 "Ssid", ns.wifi.SsidValue (ssid),
                 "ActiveProbing", ns.core.BooleanValue (False),
                 # setting blockack threshold for sta's BE queue
                 "BE_BlockAckThreshold", ns.core.UintegerValue (2),
                 # setting block inactivity timeout to 3*1024 = 3072 microseconds
                 "BE_BlockAckInactivityTimeout", ns.core.UintegerValue (3))

    staDevice = wifi.Install (phy,mac,sta)

    mac.SetType ("ns3::ApWifiMac",
                 "QosSupported", ns.core.BooleanValue (True),
                 "Ssid", ns.wifi.SsidValue (ssid),
                 "BE_BlockAckThreshold", ns.core.UintegerValue (0))

    apDevice = wifi.Install (phy, mac, ap)

    # Setting mobility model
    mobility = ns.mobility.MobilityHelper ()

    mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
                                   "MinX", ns.core.DoubleValue (0.0),
                                   "MinY", ns.core.DoubleValue (0.0),
                                   "DeltaX", ns.core.DoubleValue (5.0),
                                   "DeltaY", ns.core.DoubleValue (10.0),
                                   "GridWidth", ns.core.UintegerValue (3),
                                   "LayoutType", ns.core.StringValue ("RowFirst"))

    mobility.SetMobilityModel ("ns3::RandomWalk2dMobilityModel",
                               "Bounds", ns.mobility.RectangleValue (ns.mobility.Rectangle (-50, 50, -50, 50)))
    mobility.Install (sta)

    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
    mobility.Install (ap)

    # Internet stack
    stack = ns.internet.InternetStackHelper ()
    stack.Install (sta)
    stack.Install (ap)

    address = ns.internet.Ipv4AddressHelper ()
    address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
    staIf = ns.internet.Ipv4InterfaceContainer ()
    apIf = ns.internet.Ipv4InterfaceContainer ()
    staIf = address.Assign (staDevice)
    apIf = address.Assign (apDevice)

    # Setting applications
    port = 9
    dataRate = ns.network.DataRate ("1Mb/s")
    onOff = ns.applications.OnOffHelper ("ns3::UdpSocketFactory", ns.network.Address (ns.network.InetSocketAddress (apIf.GetAddress (0), port)))
    onOff.SetAttribute ("DataRate", ns.network.DataRateValue (dataRate))
    onOff.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0.01]"))
    onOff.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=8]"))
    onOff.SetAttribute ("PacketSize", ns.core.UintegerValue (50))

    staApps = onOff.Install (sta)

    staApps.Start (ns.core.Seconds (1.0))
    staApps.Stop (ns.core.Seconds (10.0))

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

    ns.core.Simulator.Stop (ns.core.Seconds (10.0))

    phy.EnablePcap ("wifi-blockack-py", ap.GetId (), 0)
    ns.core.Simulator.Run ()
    ns.core.Simulator.Destroy ()

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))
