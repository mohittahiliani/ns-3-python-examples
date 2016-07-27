# -*-  Mode: Python; -*-
# /*
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
#  * Ported to Python by: Mohit P. Tahiliani <tahiliani@nitk.edu.in>
#  */

import ns.core
import ns.network
import ns.internet
import ns.point_to_point
import ns.applications
import ns.point_to_point_layout

# Network topology (default)
# 
#         n2 n3 n4              .
#          \ | /                .
#           \|/                 .
#      n1--- n0---n5            .
#           /|\                 .
#          / | \                .
#         n8 n7 n6              .
# 

def main(argv):
	#
	# Set up some default values for the simulation.
	#
	ns.core.Config.SetDefault ("ns3::OnOffApplication::PacketSize", ns.core.UintegerValue (137))

	# ??? try and stick 15kb/s into the data rate
	ns.core.Config.SetDefault ("ns3::OnOffApplication::DataRate", ns.core.StringValue ("14kb/s"))

	#
	# Default number of nodes in the star. Overridable by command line argument.
	#
	cmd = ns.core.CommandLine ()
	cmd.nSpokes = 8
	cmd.AddValue ("nSpokes", "Number of nodes to place in the star")
	cmd.Parse (sys.argv)

	nSpokes = int(cmd.nSpokes)

	print "Build star topology."
	pointToPoint = ns.point_to_point.PointToPointHelper ()
	pointToPoint.SetDeviceAttribute ("DataRate", ns.core.StringValue ("5Mbps"))
	pointToPoint.SetChannelAttribute ("Delay", ns.core.StringValue ("2ms"))
	star = ns.point_to_point_layout.PointToPointStarHelper (nSpokes, pointToPoint)

	print "Install internet stack on all nodes."
	internet = ns.internet.InternetStackHelper ()
	star.InstallStack (internet)

	print "Assign IP Addresses."
	star.AssignIpv4Addresses (ns.internet.Ipv4AddressHelper (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0")))

	print "Create Applications."
	#
	# Create a packet sink on the star "hub" to receive packets.
	# 
	port = 50000
	hubLocalAddress = ns.network.Address (ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
	packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", hubLocalAddress)
	hubApp = packetSinkHelper.Install (star.GetHub ())
	hubApp.Start (ns.core.Seconds (1.0))
	hubApp.Stop (ns.core.Seconds (10.0))

	#
	# Create OnOff applications to send TCP to the hub, one on each spoke node.
	#
	onOffHelper = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", ns.network.Address ())
	onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
	onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))

	spokeApps = ns.network.ApplicationContainer ()

	for i in range(0, star.SpokeCount ()):
		remoteAddress = ns.network.AddressValue (ns.network.InetSocketAddress (star.GetHubIpv4Address (i), port))
		onOffHelper.SetAttribute ("Remote", remoteAddress)
		spokeApps = onOffHelper.Install (star.GetSpokeNode (i))

	spokeApps.Start (ns.core.Seconds (1.0))
	spokeApps.Stop (ns.core.Seconds (10.0))

	print "Enable static global routing."
	#
	# Turn on global static routing so we can actually be routed across the star.
	#
	ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

	print "Enable pcap tracing."
	#
	# Do pcap tracing on all point-to-point devices on all nodes.
	#
	pointToPoint.EnablePcapAll ("star-py")

	print "Run Simulation."
	ns.core.Simulator.Stop (ns.core.Seconds (12))
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."

if __name__ == '__main__':
    import sys
    main (sys.argv)
