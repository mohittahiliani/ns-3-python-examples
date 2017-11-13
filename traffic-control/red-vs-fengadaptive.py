import ns.core
import ns.network
import ns.internet
import ns.point_to_point
import ns.applications
import ns.point_to_point_layout
import ns.traffic_control
import sys


cmd = ns.core.CommandLine()

cmd.nLeaf = 10;
cmd.maxPackets = 100;
cmd.queueDiscLimitPackets = 1000;
cmd.queueDiscType = "RED";
cmd.pktSize = 512;
cmd.appDataRate = "10Mbps";
cmd.modeBytes  = False;
cmd.minTh = 5;
cmd.maxTh = 15;

port = 5001;
bottleNeckLinkBw = "1Mbps";
bottleNeckLinkDelay = "50ms";

cmd.AddValue ("nLeaf", "Number of left and right side leaf nodes");
cmd.AddValue ("maxPackets","Max Packets allowed in the device queue");
cmd.AddValue ("queueDiscLimitPackets","Max Packets allowed in the queue disc");
cmd.AddValue ("queueDiscType", "Set Queue disc type to RED or FengAdaptive");
cmd.AddValue ("appPktSize", "Set OnOff App Packet Size");
cmd.AddValue ("appDataRate", "Set OnOff App DataRate");
cmd.AddValue ("modeBytes", "Set Queue disc mode to Packets <false> or bytes <true>");
cmd.AddValue ("redMinTh", "RED queue minimum threshold");
cmd.AddValue ("redMaxTh", "RED queue maximum threshold");
cmd.Parse (sys.argv);

nLeaf = int(cmd.nLeaf)
maxPackets = int(cmd.maxPackets)
queueDiscLimitPackets = int(cmd.queueDiscLimitPackets)
queueDiscType = cmd.queueDiscType 
pktSize = int(cmd.pktSize)
appDataRate = cmd.appDataRate 
modeBytes = cmd.modeBytes
minTh = int(cmd.minTh)
maxTh = int(cmd.maxTh)

if ((queueDiscType != "RED") and (queueDiscType != "FengAdaptive")):
	print "Invalid queue disc type: Use --queueDiscType=RED or --queueDiscType=FengAdaptive"
	sys.exit(1)

ns.core.Config.SetDefault ("ns3::OnOffApplication::PacketSize", ns.core.UintegerValue (pktSize))
ns.core.Config.SetDefault ("ns3::OnOffApplication::DataRate", ns.core.StringValue (appDataRate))

ns.core.Config.SetDefault ("ns3::QueueBase::Mode", ns.core.StringValue ("QUEUE_MODE_PACKETS"))
ns.core.Config.SetDefault ("ns3::QueueBase::MaxPackets", ns.core.UintegerValue (maxPackets))


if (modeBytes == "False"):
	ns.core.Config.SetDefault ("ns3::RedQueueDisc::Mode", ns.core.StringValue ("QUEUE_DISC_MODE_PACKETS"));
	ns.core.Config.SetDefault ("ns3::RedQueueDisc::QueueLimit", ns.core.UintegerValue (queueDiscLimitPackets));
else:
	ns.core.Config.SetDefault ("ns3::RedQueueDisc::Mode", ns.core.StringValue ("QUEUE_DISC_MODE_BYTES"));
	ns.core.Config.SetDefault ("ns3::RedQueueDisc::QueueLimit", ns.core.UintegerValue (queueDiscLimitPackets * pktSize));
	minTh *= pktSize;
	maxTh *= pktSize;

ns.core.Config.SetDefault ("ns3::RedQueueDisc::MinTh", ns.core.DoubleValue (minTh));
ns.core.Config.SetDefault ("ns3::RedQueueDisc::MaxTh", ns.core.DoubleValue (maxTh));
ns.core.Config.SetDefault ("ns3::RedQueueDisc::LinkBandwidth", ns.core.StringValue (bottleNeckLinkBw));
ns.core.Config.SetDefault ("ns3::RedQueueDisc::LinkDelay", ns.core.StringValue (bottleNeckLinkDelay));
ns.core.Config.SetDefault ("ns3::RedQueueDisc::MeanPktSize", ns.core.UintegerValue (pktSize));

if (queueDiscType == "FengAdaptive"):
	# Turn on Feng's Adaptive RED
	ns.core.Config.SetDefault ("ns3::RedQueueDisc::FengAdaptive", ns.core.BooleanValue (True));

# Create the point-to-point link helpers
bottleNeckLink = ns.point_to_point.PointToPointHelper (); 
bottleNeckLink.SetDeviceAttribute  ("DataRate", ns.core.StringValue (bottleNeckLinkBw));
bottleNeckLink.SetChannelAttribute ("Delay", ns.core.StringValue (bottleNeckLinkDelay));

pointToPointLeaf = ns.point_to_point.PointToPointHelper ();
pointToPointLeaf.SetDeviceAttribute    ("DataRate", ns.core.StringValue ("10Mbps"));
pointToPointLeaf.SetChannelAttribute   ("Delay", ns.core.StringValue ("1ms"));

d = ns.point_to_point_layout.PointToPointDumbbellHelper (nLeaf, pointToPointLeaf, nLeaf, pointToPointLeaf, bottleNeckLink);

# Install Stack
stack = ns.internet.InternetStackHelper ();
for i in range(d.LeftCount ()):
	stack.Install (d.GetLeft (i));

for i in range(d.RightCount ()):
	stack.Install (d.GetRight (i));

stack.Install (d.GetLeft ())
stack.Install (d.GetRight ())

tchBottleneck = ns.traffic_control.TrafficControlHelper ()
queueDiscs = ns.traffic_control.QueueDiscContainer ()
tchBottleneck.SetRootQueueDisc ("ns3::RedQueueDisc")
tchBottleneck.Install (d.GetLeft ().GetDevice (0))
queueDiscs = tchBottleneck.Install (d.GetRight ().GetDevice (0))
