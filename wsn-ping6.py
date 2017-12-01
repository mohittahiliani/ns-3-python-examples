#/* -*-  Mode: Python; -*- */
#/*
# * Copyright (c) 2017 NITK surathkal
# *
# * This program is free software you can redistribute it and/or modify
# * it under the terms of the GNU General Public License version 2 as
# * published by the Free Software Foundation
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# *
# * Ported to Python by: Abhilash Sanap <ssabhilash24@gmail.com>
# */

#// Network topology
#//
#//       n0    n1
#//       |     |
#//       =================
#//        WSN (802.15.4)
#//
#// - ICMPv6 echo request flows from n0 to n1 and back with ICMPv6 echo reply
#// - DropTail queues 
#// - Tracing of queues and packet receptions to file "wsn-ping6.tr"
#//
#// This example is based on the "ping6.cc" example.

import ns.core
import ns.network
import ns.internet
import ns.applications
import sys
import ns
import ns3.lr-wpan
import ns.internet-apps
import ns.mobility
import ns.lr-wpan

print "Ping6WsnExample"

verbose = False

cmd = ns.core.CommandLine()
cmd.AddValue ("verbose", "turn on log components")
cmd.Parse (sys.argv)

if (verbose):

	ns.core.LogComponentEnable ("Ping6WsnExample", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable ("Ipv6EndPointDemux", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)      
	ns.core.LogComponentEnable ("Ipv6ListRouting", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("NdiscCache", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("SixLowPanNetDevice", ns.core.LOG_LEVEL_ALL)


print "Create nodes."
nodes = ns.network.NodeContainer()
nodes.Create(2)

 #Set seed for random numbers

 ns.core.SeedManager.SetSeed (167)

  # Install mobility

mobility=ns.network.MobilityHelper ()
mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

nodesPositionAlloc = ns.network.ListPositionAllocator.CreateObject<ListPositionAllocator> ()
nodesPositionAlloc.Add(Vector (0.0, 0.0, 0.0))
nodesPositionAlloc.Add(Vector (50.0, 0.0, 0.0))
mobility.SetPositionAllocator (nodesPositionAlloc)
mobility.Install (nodes)

print "Create channels."

lrWpanHelper = ns.network.LrWpanhelper()

devContainer = lrWpanHelper.Install(nodes)
lrWpanHelper.AssociateToPan (devContainer,10)

# Add and install the LrWpanNetDevice for each node

print "Created "+devContainer.GetN()+" devices\n"
print "There are "+nodes.GetN()+" nodes\n"

# Install IPv4/IPv6 stack

print "Install Internet Stack."

internetv6 = ns.internet.InternetStackHelper()
internetv6.SetIpv4StackInstall (False)
internetv6.Install (nodes)

# Install 6LowPan Layer

print "Install 6LowPAN."

sixlowpan = ns.internet.SixLowPanHelper()
six1 = sixlowpan.Install (devContainer)

print "Assign addresses."

ipv6=ns.internet.Ipv6AddressHelper()
ipv6.SetBase (Ipv6Address ("2001:1::"), Ipv6Prefix (64))

i = ns.internet.Ipv6InterfaceContainer()
i = ipv6.Assign(six1)

print "Create Applications."

# Create a Ping6 application to send ICMPv6 echo request from node zero to
#   all-nodes (ff02::1).
   

cmd.packetSize = 10
cmd.maxPacketCount = 5

interPacketInterval = ns.core.TimeValue(ns.core.Seconds (1.))
ping6 = ns.applications.PingHelper ()

ping6.SetLocal (i.GetAddress (0, 1))
ping6.SetRemote (i.GetAddress (1, 1))
  
ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))

apps = ns.network.ApplicationContainer()
apps = ping6.Install(nodes.Get(0))

apps.Start (ns.core.Seconds (2.0))
apps.Stop (ns.core.Seconds (10.0))

Ascii = ns.applications.AsciiTraceHelper() 
lrWpanHelper.EnableAsciiAll (Ascii.CreateFileStream ("ping6wsn.tr"))
lrWpanHelper.EnablePcapAll (std::string ("ping6wsn"), True)

print "Run Simulation."

ns.core.Simulator.Run ()
ns.core.Simulator.Destroy ()

print "Done."
