#/* -*-  Mode: Python; -*- */
#/*
# * Copyright (c) 2017 NITK Surathkal
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License version 2 as
# * published by the Free Software Foundation;
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# *
# * Ported to Python by: Akshay Anandrao Honrao <eakshay97honrao@gmail.com>
# */


# Network topology
#
#             STA2
#              |
#              |
#   R1         R2
#   |          |
#   |          |
#   ------------
#           |
#           |
#          STA 1
#
# - Initial configuration :
#         - STA1 default route : R1
#         - R1 static route to STA2 : R2
#         - STA2 default route : R2
# - STA1 send Echo Request to STA2 using its default route to R1
# - R1 receive Echo Request from STA1, and forward it to R2
# - R1 send an ICMPv6 Redirection to STA1 with Target STA2 and Destination R2
# - Next Echo Request from STA1 to STA2 are directly sent to R2


import ns.network
import ns.core
import ns.applications
import ns.internet
import ns.internet_apps
import ns.csma
import sys

cmd = ns.core.CommandLine()
cmd.AddValue ("verbose", "turn on log components")
cmd.Parse(sys.argv)

if verbose == "True":
	ns.core.LogComponentEnable("Icmpv6RedirectExample", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("Icmpv6L4Protocol", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("NdiscCache", ns.core.LOG_LEVEL_ALL)

print "Creat nodes."
stal = ns.nodes.CreatObject()
r1 = ns.nodes.CreatObject()
r2 = ns.nodes.CreatObject()
sta2 = ns.nodes.CreatObject()

net1 = ns.network.NodeContainer(stal, r1, r2)
net2 = ns.network.NodeContainer(r2, sta2)
all1 = ns.network.NodeContainer(stal, r1, r2, sta2)  #all is python keyword hence all1 is used instead of all. 

internetv6 = ns.internet.InternetStackHelper()
internetv6.Install(all1)

print "Create channels."
csma = ns.csma.CsmaHelper()
csma.SetChannelAttribute("DataRate", ns.core.DataRateValue (5000000))
csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(6560)))
ndc1 = csma.Install(net1)
ndc2 = csma.Install(net2)

print "Assign IPv6 Addresses."
ipv6 = ns.internet.Ipv6AddressHelper()

ipv6.SetBase (ns.network.Ipv6Address ("2001:1::"), ns.network.Ipv6Prefix (64))
iic1 = ipv6.Assign (ndc1)
iic1.SetForwarding (2, True)
iic1.SetForwarding (1, True)
iic1.SetDefaultRouteInAllNodes (1)

ipv6.SetBase (ns.network.Ipv6Address ("2001:2::"), ns.network.Ipv6Prefix (64))
iic2 = ipv6.Assign (ndc2)
iic2.SetForwarding (0, True)
iic1.SetDefaultRouteInAllNodes (0)

routingHelper = ns.internet.Ipv6StaticRoutingHelper()

# manually inject a static route to the second router.
routing = ns.internet.Ipv6StaticRouting()
routing = routingHelper.GetStaticRouting (r1.GetObject())
routing.AddHostRouteTo (iic2.GetAddress (1, 1), iic1.GetAddress (2, 0), iic1.GetInterfaceIndex (1))

routingStream = ns.internet.OutputStreamWrapper()
routingHelper.PrintRoutingTableAt (ns.core.Seconds (0.0), r1, routingStream)
routingHelper.PrintRoutingTableAt (ns.core.Seconds (3.0), sta1, routingStream)

print "Create Applications."
cmd.packetSize = 1024
cmd.maxPacketCount = 5
interPacketInterval = ns.core.Seconds (1.)
ping6 = ns.applications.Ping6Helper()

ping6.SetLocal (iic1.GetAddress (0, 1))
ping6.SetRemote (iic2.GetAddress (1, 1))
ping6.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
ping6.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
ping6.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))
apps = ns.network.ApplicationContainer()
apps = ping6.Install(stal)
apps.Start (ns.core.Seconds (2.0))
apps.Stop (ns.core.Seconds (10.0))

Ascii = ns.internet.AsciiTraceHelper()
csma.EnableAsciiAll (Ascii.CreateFileStream ("icmpv6-redirect.tr"))
csma.EnablePcapAll ("icmpv6-redirect", True)

print "Run Simulation."
ns.core.Simulator.Run ()
ns.core.Simulator.Destroy ()
print "Done."