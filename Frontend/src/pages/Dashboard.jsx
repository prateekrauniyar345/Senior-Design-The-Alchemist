import React from 'react';
import { Container, Navbar, Nav, Button, Row, Col, Card, Table, Badge } from 'react-bootstrap';
import { LogIn, UserPlus, Sparkles, Activity, CheckCircle, Clock, Zap } from 'lucide-react';
import Header from '../components/shared/header';

const Dashboard = () => {
    const gradientTextStyle = {
        background: 'linear-gradient(90deg, #00BFFF, #ff1493)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontWeight: '700',
    };

    const snapshotData = [
        { title: "Total Runs", value: "1,452", icon: Activity, color: "light" },
        { title: "Success Rate", value: "98.5%", icon: CheckCircle, color: "info" },
        { title: "Avg. Latency", value: "3.1 s", icon: Clock, color: "secondary" },
        { title: "Mindat Status", value: "Online", icon: Zap, color: "light" },
    ];

    const traceData = [
        { summary: "Plot element distribution in pyrites.", agent: "Histogram_Plotter", duration: "4.1s", status: "SUCCESS", traceId: "f478a", statusColor: "success" },
        { summary: "Show network of copper minerals.", agent: "Network_Plotter", duration: "2.9s", status: "SUCCESS", traceId: "c91b2", statusColor: "success" },
        { summary: "Heatmap of silver localities in Asia.", agent: "Heatmap_Plotter", duration: "5.8s", status: "FAILED", traceId: "a04d3", statusColor: "danger" },
    ];

    return (
        <div className="min-vh-100 position-relative overflow-hidden" style={{ background: '#0a0a0a' }}>
            <div style={{
                position: 'absolute',
                top: '-150px',
                right: '-150px',
                width: '400px',
                height: '400px',
                background: 'radial-gradient(circle, rgba(6, 182, 212, 0.2), transparent 70%)',
                borderRadius: '50%',
                pointerEvents: 'none'
            }}></div>
            
            <div style={{
                position: 'absolute',
                bottom: '-200px',
                left: '-200px',
                width: '450px',
                height: '450px',
                background: 'radial-gradient(circle, rgba(255, 20, 147, 0.15), transparent 70%)',
                borderRadius: '50%',
                pointerEvents: 'none'
            }}></div>

            <div className="position-relative" style={{ zIndex: 1 }}>
                <Container fluid className="w-100 px-5">

                   <Header />
                    
                    {/* Hero - takes 70-80% of screen */}
                    <div 
                        className="d-flex flex-column justify-content-center align-items-center text-center" 
                        style={{ minHeight: '60vh' }}
                    >
                        <p className="text-uppercase mb-3 fs-4" style={{ color: '#06b6d4', letterSpacing: '0.1em' }}>
                            Revolutionize Mineral Exploration
                        </p>
                        <h1 className="fw-bold text-white mb-4" style={{ fontSize: 'clamp(3rem, 6vw, 5rem)', lineHeight: '1.1' }}>
                            Creative <span style={gradientTextStyle}>Data Projects</span><br />with AI-Powered Agents
                        </h1>
                        <p className="text-secondary mb-5 mx-auto fs-4" style={{ maxWidth: '800px' }}>
                            Next-gen platform for querying and visualizing mineralogical data from Mindat.org using LangChain and LangGraph.
                        </p>
                        
                        <div className="d-flex align-items-center gap-3">
                            <Button 
                                href="/chat" 
                                size="lg"
                                className="fw-semibold d-inline-flex align-items-center px-5 py-3 fs-4"
                                style={{ 
                                    backgroundColor: 'black',
                                    boxShadow: '0 0 15px rgba(152, 152, 152, 0.6)', 
                                    border: '0.5px solid #06b6d4',
                                }}
                            >
                                <Sparkles size={24} className="me-2" />
                                Start New Query
                            </Button>
                            <span className="text-secondary fs-5">
                                1,452 runs this week
                            </span>
                        </div>
                    </div>

                    {/* Snapshot Cards */}
                    <div className="my-5 py-5">
                        <h2 className="fw-semibold text-center text-white mb-5" style={{ fontSize: '2.5rem' }}>
                            Agent Performance
                        </h2>
                        <Row className="g-4 justify-content-center">
                            {snapshotData.map((item) => (
                                <Col sm={6} lg={3} key={item.title}>
                                    <Card className="border-0 h-100" style={{ backgroundColor: '#1a1a1a', borderRadius: '12px' }}>
                                        <Card.Body className="p-4">
                                            <div className="d-flex justify-content-between align-items-start mb-3">
                                                <p className="text-white mb-0 fs-5">{item.title}</p>
                                                <item.icon size={28} style={{ color: item.color === 'info' ? '#06b6d4' : '#f8fafc' }} />
                                            </div>
                                            {item.title === "Mindat Status" ? (
                                                <div className="d-flex align-items-center">
                                                    <div className="rounded-circle bg-success me-2" style={{ width: '0.8rem', height: '0.8rem' }}></div>
                                                    <p className="h3 fw-bold mb-0" style={{ color: '#06b6d4' }}>Online</p>
                                                </div>
                                            ) : (
                                                <p className="h1 fw-bold text-white mb-0">{item.value}</p>
                                            )}
                                        </Card.Body>
                                    </Card>
                                </Col>
                            ))}
                        </Row>
                    </div>
                    
                    {/* Traces Table */}
                    <div className="mb-5 pb-5">
                        <h2 className="fw-semibold text-white mb-4" style={{ fontSize: '2.5rem' }}>
                            Recent Traces
                        </h2>
                        <Card className="border-0" style={{ backgroundColor: '#1a1a1a', borderRadius: '12px' }}>
                            <Card.Body className="p-4">
                                <Table borderless hover variant="dark">
                                    <thead>
                                        <tr className="text-muted fs-5">
                                            <th className="px-3 py-3">Query</th>
                                            <th className="px-3 py-3">Agent</th>
                                            <th className="px-3 py-3">Duration</th>
                                            <th className="px-3 py-3">Status</th>
                                            <th className="px-3 py-3">ID</th>
                                        </tr>
                                    </thead>
                                    <tbody className="fs-5">
                                        {traceData.map((trace, i) => (
                                            <tr key={i} className="text-white">
                                                <td className="px-3 py-3">{trace.summary}</td>
                                                <td className="px-3 py-3" style={{ color: '#06b6d4' }}>{trace.agent}</td>
                                                <td className="px-3 py-3 text-secondary">{trace.duration}</td>
                                                <td className="px-3 py-3">
                                                    <Badge bg={trace.statusColor} className="fs-6 px-3 py-2">{trace.status}</Badge>
                                                </td>
                                                <td className="px-3 py-3 text-info">{trace.traceId}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </Table>
                            </Card.Body>
                        </Card>
                    </div>
                </Container>
            </div>
        </div>
    );
};

export default Dashboard;