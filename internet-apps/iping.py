import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.internet_apps
import ns.point_to_point
import sys

cmd = ns.core.CommandLine()
cmd.c = 4294967295
cmd.t = 0
cmd.i = 1.0
cmd.w = 15.0
cmd.s = 56
cmd.v = False
cmd.q = False

cmd.AddValue("c", "Stops after sending specified number(count) of ECHO_REQUEST packets.")
cmd.AddValue("i", "Specify the interval seconds between sending each packet.")
cmd.AddValue("t", "Set the IP Time to Live.")
cmd.AddValue("w", "Specify a timeout, in seconds, before ping exits regardless  of  how  many  packets have  been sent or received.")
cmd.AddValue("s", "Specifies the number of data bytes to be sent.")
cmd.AddValue("v", "Verbose output.")
cmd.AddValue("q", "Quiet output.  Nothing is displayed except the summary lines at  startup  time  and when finished.")

cmd.Parse(sys.argv)

count = int(cmd.c)
ttl = int(cmd.t)
deadline = float(cmd.w)
packetsize = int(cmd.s)
interval = float(cmd.i)
verbose = bool(cmd.v)
quiet = bool(cmd.q)

if count <=0:
	print ("ping: bad number of packets to transmit.")
	sys.exit(1)
if interval < 0:
	print ("ping: bad timing interval.")
	sys.exit(1)
if ttl < 0:
	print ("ping: bad value.")
	sys.exit(1)
if packetsize < 0:
	print ("ping: illegal negetive packet size.")
	sys.exit(1)
if interval < 0.2 and interval >= 0 :
	print ("ping: cannot flood minimal interval allowed for user is 200ms.")
	sys.exit(1)

c = ns.network.NodeContainer()
c.Create (2)

pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute ("DataRate", ns.core.StringValue ("5Mbps"))
pointToPoint.SetChannelAttribute ("Delay", ns.core.StringValue ("2ms"))

devices = ns.network.NetDeviceContainer()
devices = pointToPoint.Install(c)

address = ns.internet.Ipv4AddressHelper()
address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
stack = ns.internet.InternetStackHelper()
stack.Install(c)

interfaces = ns.internet.Ipv4InterfaceContainer()
interfaces = address.Assign(devices)

app = ns.internet_apps.V4Ping()

app.SetAttribute ("Remote", ns.network.Ipv4AddressValue (interfaces.GetAddress(1)))
app.SetAttribute ("Verbose", ns.core.BooleanValue (verbose))
app.SetAttribute ("Count", ns.core.UintegerValue (count))
app.SetAttribute ("Ttl", ns.core.UintegerValue (ttl))     
app.SetAttribute ("Quiet", ns.core.BooleanValue (quiet) )     
app.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Seconds (interval)) )
app.SetAttribute ("Size", ns.core.UintegerValue (packetsize))

c.Get(0).AddApplication(app)

app.SetStartTime(ns.core.Seconds(1.0))
app.SetStopTime(ns.core.Seconds(1.0 + deadline))

pointToPoint.EnablePcapAll("iping", False)

ns.core.Simulator.Run()
ns.core.Simulator.Destroy()





