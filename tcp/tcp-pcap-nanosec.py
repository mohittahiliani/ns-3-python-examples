# /*
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
#  * Ported to Python by:
#  * Adarsh Honawad <adarsh2397@gmail.com>
#  * Sagar Bharadwaj <sagarbharadwaj50@gmail.com>
#  * Samvid Dharanikota <samvid25@yahoo.com>		
#  */

# // Python version of "tcp-pcap-nanosec-example.cc"
# // Network topology
# //
# //       n0 ----------- n1
# //            500 Kbps
# //             5 ms
# //
# // - Flow from n0 to n1 using BulkSendApplication.
# // - Tracing of queues and packet receptions to file "tcp-pcap-nanosec-example_py.pcap"
# //


# // ============================================================ //
# // NOTE: You can check the "magic" number of a pcap file with   //
# //       the following command:                                 //
# //                                                              //
# //                    od -N4 -tx1 filename.pcap                 //
# //                                                              //
# // ============================================================ //

import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point

# //
# // Explicitly create the nodes required by the topology (shown above).
# //
nodes = ns.network.NodeContainer()
nodes.Create(2)

# //
# // Explicitly create the point-to-point link required by the topology (shown above).
# //
pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute("DataRate", ns.core.StringValue("500Kbps"))
pointToPoint.SetChannelAttribute("Delay", ns.core.StringValue("5ms"))

devices = pointToPoint.Install(nodes)

# //
# // Install the internet stack on the nodes
# //
stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

# //
# // We've got the "hardware" in place.  Now we need to add IP addresses.
# //
address = ns.internet.Ipv4AddressHelper()
address.SetBase(ns.network.Ipv4Address("10.1.1.0"),
                ns.network.Ipv4Mask("255.255.255.0"))

interfaces = address.Assign(devices)

# //
# // Create a BulkSendApplication and install it on node 0
# //
source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory",
                     ns.network.InetSocketAddress (interfaces.GetAddress (1), 9)) # well-known echo port number

# // Set the amount of data to send in bytes.  Zero is unlimited.
source.SetAttribute ("MaxBytes", ns.core.UintegerValue (0))
sourceApps = source.Install (nodes.Get (0))
sourceApps.Start (ns.core.Seconds (0.0))
sourceApps.Stop (ns.core.Seconds (10.0))

# //
# // Create a PacketSinkApplication and install it on node 1
# //
sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory",
                     ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), 9))
sinkApps = sink.Install (nodes.Get (1))
sinkApps.Start (ns.core.Seconds (0.0))
sinkApps.Stop (ns.core.Seconds (10.0))

pointToPoint.EnablePcapAll ("tcp-pcap-nanosec-example-py")

# //
# // Now, do the actual simulation.
# //
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()
