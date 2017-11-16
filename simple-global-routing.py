# -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# Network topology
#
#  n0
#     \ 5 Mb/s, 2ms
#      \          1.5Mb/s, 10ms
#       n2 -------------------------n3
#      /
#     / 5 Mb/s, 2ms
#   n1
#
# - all links are point-to-point links with indicated one-way BW/delay
# - CBR/UDP flows from n0 to n3, and from n3 to n1
# - FTP/TCP flow from n0 to n3, starting at time 1.2 to time 1.35 sec.
# - UDP packet size of 210 bytes, with per-packet interval 0.00375 sec.
#   (i.e., DataRate of 448,000 bps)
# - DropTail queues 
# - Tracing of queues and packet receptions to file "simple-global-routing.tr"

import ns.internet_apps
import ns.core
import ns.network
import ns.internet
import ns.point_to_point
import ns.applications
import ns.internet
import ns.csma
import ns.flow_monitor_helper
import ipv4_global_routing_helper

def main (argv):
	# 
	# Users may find it convenient to turn on explicit debugging
	# 
	
	# Set up some default values for the simulation
	#Config::SetDefault ("ns3::OnOffApplication::PacketSize", UintegerValue (210));
	#Config::SetDefault ("ns3::OnOffApplication::DataRate", StringValue ("448kb/s"));

	#
	# DefaultValue::Bind ("DropTailQueue::m_maxPackets", 30);
	# Allow the user to override any of the defaults and the above
	# DefaultValue::Bind ()s at run-time, via command-line arguments
	#
	cmd = ns.core.CommandLine ()
	cmd.enableFlowMonitor = "False"
	cmd.AddValue ("EnableMonitor", "Enable Flow Monitor", enableFlowMonitor)
	cmd.Parse (sys.argv)

	#
	# Explicitly create the nodes required by the topology (shown above).
	# 
	print "Create nodes."
	c = ns.network.NodeContainer ()
	c.Create (4)
	n0n2 = ns.network.NodeContainer (c.Get (0), c.Get (2))
	n1n2 = ns.network.NodeContainer (c.Get (1), c.Get (2))
	n3n2 = ns.network.NodeContainer (c.Get (3), c.Get (2))

	# 
	# Install the internet stack on the nodes
	# 
	stack = ns.internet.InternetStackHelper ()
	stack.Install (c)

	#
	# We create the channels first without any IP addressing information
	#
	print "Create channels."
	p2p = ns.point_to_point.PointToPointHelper ()
	p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("5Mbps"))
	p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("2ms"))
	d0d2 = p2p.Install (n0n2);
	d1d2 = p2p.Install (n1n2);
	p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("1500kbps"));
	p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("10ms"));
 	d3d2 = p2p.Install (n3n2);

	#
	# Now, we add IP addresses.
	#
	print "Assign IP Addresses."
	ipv4 = ns.internet.Ipv4AddressHelper ()
	ipv4.SetBase (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	i0i2 = ipv4.Assign (d0d2)
	ipv4.SetBase (ns.network.Ipv4Address ("10.1.2.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	i1i2 = ipv4.Assign (d1d2)
        ipv4.SetBase (ns.network.Ipv4Address ("10.1.3.0"), ns.network.Ipv4Mask ("255.255.255.0"))
        i3i2 = ipv4.Assign (d3d2)
	
	#
	# Create router nodes, initialize routing database and set up the routing
	# tables in the nodes.
	#
        ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

	#
	# Create the OnOff application to send UDP datagrams of size
	# 210 bytes at a rate of 448 Kb/s
	#
	print "Create Applications."
	# 
	# Create a BulkSendApplication and install it on node 0
	# 
	port = 9  # well-known echo port number

	onoff = ns.applications.OnOffHelper ("ns3::UdpSocketFactory", ns.network.InetSocketAddress (i3i2.GetAddress (0), port))
	
	# Set the amount of data to send in bytes.  Zero is unlimited. ?
	onoff.SetConstantRate (DataRate ("448kb/s"))
	apps = onoff.Install (c.Get (0))
	apps.Start (ns.core.Seconds (1.0))
	apps.Stop (ns.core.Seconds (10.0))
	
	##onoff.SetConstantRate (DataRate ("448kb/s"));

	# 
	# Create a packet sink to receive these packets
	# 
	sink = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory", ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
	apps = sink.Install (c.Get (3))
	apps.Start (ns.core.Seconds (1.0))
	apps.Stop (ns.core.Seconds (10.0))

	#
	# Create a similar flow from n3 to n1, starting at time 1.1 seconds
	#
	onoff.SetAttribute ("Remote", ns.network.InetSocketAddress (i1i2.GetAddress (0), port))
        apps = onoff.Install (c.Get (3));
        apps.Start (Seconds (1.1));
        apps.Stop (Seconds (10.0));

        #
        # Create a packet sink to receive these packets
        #
        apps = sink.Install (c.Get (1));
        apps.Start (Seconds (1.1));
        apps.Stop (Seconds (10.0));

	ascii = ns.network.AsciiTraceHelper ()
        p2p.EnableAsciiAll (ascii.CreateFileStream ("simple-global-routing.tr"))
	p2p.EnablePcapAll ("simple-global-routing")

	#
	#Flow Monitor
	#
	flowmonHelper = ns.flow_monitor.FlowMonitorHelper ()
	if (enableFlowMonitor):
		   monitor = flowmonHelper.InstallAll()

	# 
	# Now, do the actual simulation.
	# 
	print "Run Simulation."
	ns.core.Simulator.Stop (ns.core.Seconds (11))
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."


	if (enableFlowMonitor):
		flowmonHelper.SerializeToXmlFile ("simple-global-routing.flowmon", False, False)
    

	# ns.core.Simulator.Destroy ()
if __name__ == '__main__':
    import sys
    main (sys.argv)
