import React, { useState, useEffect } from 'react';
import { Upload, Truck, Search, ArrowRight, AlertCircle, Database, MapPin, CheckCircle, RefreshCw, Trash2, Pencil, X, Save, Package, Plus, Share2, Activity, FileText } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [view, setView] = useState('landing'); 
  const [dbStatus, setDbStatus] = useState('loading'); 
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/status/`);
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      setDbStatus(data.data_exists ? 'has_data' : 'empty');
    } catch (err) {
      console.error("API Error:", err);
      setDbStatus('empty'); 
      showNotify("Could not connect to Backend API", "error");
    }
  };

  const showNotify = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-emerald-200">
      <nav className="bg-emerald-900 text-white p-4 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2 cursor-pointer hover:opacity-90 transition-opacity" onClick={() => setView('landing')}>
            <Truck className="h-6 w-6" />
            <span className="text-xl font-bold tracking-tight">BD LogisticsFlow</span>
          </div>
          <div className="hidden md:flex items-center gap-4 text-sm opacity-80">
            <span>Max-Flow & Knapsack System</span>
            {view === 'app' && (
              <button onClick={checkStatus} className="hover:text-white hover:opacity-100 transition-all" title="Refresh Connection">
                <RefreshCw size={16} />
              </button>
            )}
          </div>
        </div>
      </nav>

      {notification && (
        <div className={`fixed top-20 right-5 z-50 px-6 py-4 rounded-xl shadow-2xl text-white animate-bounce flex items-center gap-3 font-medium ${notification.type === 'error' ? 'bg-rose-500' : 'bg-emerald-600'}`}>
          {notification.type === 'error' ? <AlertCircle size={20}/> : <CheckCircle size={20}/>}
          {notification.msg}
        </div>
      )}

      <main className="container mx-auto p-4 md:p-8">
        {view === 'landing' ? (
          <LandingPage onStart={() => setView('app')} />
        ) : (
          <Dashboard 
            status={dbStatus} 
            refreshStatus={checkStatus} 
            notify={showNotify}
          />
        )}
      </main>
    </div>
  );
}

function LandingPage({ onStart }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
      <div className="bg-emerald-100 p-8 rounded-full mb-8 shadow-inner">
        <Truck className="h-16 w-16 text-emerald-700" />
      </div>
      <h1 className="text-4xl md:text-6xl font-extrabold text-slate-800 mb-6 tracking-tight">
        Bangladesh Supply Chain <br/>
        <span className="text-emerald-600">Optimization Network</span>
      </h1>
      <p className="text-lg text-slate-600 max-w-2xl mb-12 leading-relaxed">
        Analyze maximum transport capacity and optimize resource allocation using Max-Flow and Knapsack algorithms.
      </p>
      <button 
        onClick={onStart}
        className="group bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-bold py-4 px-10 rounded-full shadow-xl hover:shadow-2xl transition-all flex items-center gap-3 mx-auto transform hover:-translate-y-1"
      >
        Start Optimization
        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </button>
    </div>
  );
}

function Dashboard({ status, refreshStatus, notify }) {
  const [activeTab, setActiveTab] = useState('calculator');
  
  // Lifted state to persist results across tabs
  const [calculationResult, setCalculationResult] = useState(null);
  const [allocationResult, setAllocationResult] = useState(null);

  if (status === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-emerald-600">
        <RefreshCw className="w-10 h-10 animate-spin mb-4" />
        <p className="font-medium text-lg">Connecting to logistics network...</p>
      </div>
    );
  }

  if (status === 'empty') {
    return <CsvUploader onUploadSuccess={() => { refreshStatus(); notify("Data uploaded successfully!"); }} notify={notify} />;
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Navigation Tabs */}
      <div className="flex flex-wrap justify-center mb-8 gap-2">
        <div className="bg-white p-1 rounded-xl shadow-sm border border-slate-200 inline-flex flex-wrap justify-center">
          <TabButton active={activeTab === 'calculator'} onClick={() => setActiveTab('calculator')} icon={<Search size={16}/>} label="Calculator" />
          <TabButton active={activeTab === 'graph'} onClick={() => setActiveTab('graph')} icon={<Share2 size={16}/>} label="Network Graph" />
          <TabButton active={activeTab === 'data'} onClick={() => setActiveTab('data')} icon={<Database size={16}/>} label="Transport Data" />
          <TabButton active={activeTab === 'resources'} onClick={() => setActiveTab('resources')} icon={<Package size={16}/>} label="Resources" />
        </div>
      </div>

      <div className="animate-fade-in-up">
        {activeTab === 'calculator' && (
          <FlowCalculator 
            notify={notify} 
            result={calculationResult} 
            setResult={setCalculationResult}
            allocation={allocationResult}
            setAllocation={setAllocationResult}
          />
        )}
        {activeTab === 'graph' && (
          <NetworkGraphView 
            notify={notify} 
            result={calculationResult} 
          />
        )}
        {activeTab === 'data' && <DataManager notify={notify} refreshStatus={refreshStatus} />}
        {activeTab === 'resources' && <ResourceManager notify={notify} />}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }) {
  return (
    <button 
      onClick={onClick}
      className={`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${active ? 'bg-emerald-100 text-emerald-800 shadow-sm' : 'text-slate-500 hover:text-emerald-600 hover:bg-slate-50'}`}
    >
      {icon} {label}
    </button>
  );
}

/* --- 1. NETWORK GRAPH COMPONENT --- */
function NetworkGraphView({ notify, result }) {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_BASE}/flows/`);
        if (!res.ok) throw new Error("Failed");
        const data = await res.json();
        processGraph(data);
      } catch (e) {
        notify("Failed to load graph data", "error");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const processGraph = (data) => {
    const uniqueNodes = new Set();
    data.forEach(d => { uniqueNodes.add(d.A); uniqueNodes.add(d.to); });
    
    const nodeList = Array.from(uniqueNodes);
    const radius = 250;
    const centerX = 400;
    const centerY = 300;
    
    const processedNodes = nodeList.map((name, i) => {
      const angle = (i / nodeList.length) * 2 * Math.PI;
      return {
        id: name,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    setNodes(processedNodes);
    setLinks(data);
  };

  const getFlowValue = (u, v) => {
    if (!result || !result.details) return 0;
    return result.details[u]?.[v] || 0;
  };

  if (loading) return <div className="text-center py-20 text-slate-400">Loading visualization...</div>;

  return (
    <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="bg-slate-50 p-6 border-b border-slate-200 flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-600" /> Network Topology
          </h3>
          <p className="text-sm text-slate-500">
            {result ? `Visualizing flow from ${result.source} to ${result.sink}` : 'Showing all routes and capacities'}
          </p>
        </div>
        {result && (
          <div className="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-bold">
            Total Flow: {result.max_flow}
          </div>
        )}
      </div>
      
      <div className="p-4 overflow-auto flex justify-center bg-slate-900">
        <svg width="800" height="600" className="bg-slate-900 rounded-xl select-none">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="28" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
            </marker>
            <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="28" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#10b981" />
            </marker>
          </defs>
          
          {/* Edges */}
          {links.map((link, i) => {
            const source = nodes.find(n => n.id === link.A);
            const target = nodes.find(n => n.id === link.to);
            if (!source || !target) return null;

            const flow = getFlowValue(link.A, link.to);
            const isActive = flow > 0;

            return (
              <g key={i}>
                <line 
                  x1={source.x} y1={source.y} 
                  x2={target.x} y2={target.y} 
                  stroke={isActive ? "#10b981" : "#475569"} 
                  strokeWidth={isActive ? "3" : "1.5"}
                  markerEnd={`url(#${isActive ? 'arrowhead-active' : 'arrowhead'})`}
                  opacity={isActive ? "1" : "0.4"}
                />
                
                {/* Capacity Label */}
                <rect 
                  x={(source.x + target.x) / 2 - 20} 
                  y={(source.y + target.y) / 2 - 15} 
                  width="40" height="20" 
                  rx="4"
                  fill={isActive ? "#064e3b" : "#1e293b"}
                  opacity="0.8"
                />
                <text 
                  x={(source.x + target.x) / 2} 
                  y={(source.y + target.y) / 2} 
                  fill={isActive ? "#fff" : "#94a3b8"} 
                  fontSize="10" 
                  fontWeight="bold"
                  textAnchor="middle"
                  dy="-1"
                >
                  {isActive ? `${flow}/${link.max_capacity}` : link.max_capacity}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const isSource = result?.source === node.id;
            const isSink = result?.sink === node.id;
            let nodeColor = "#10b981"; 
            if (isSource) nodeColor = "#3b82f6";
            if (isSink) nodeColor = "#f43f5e";

            return (
              <g key={node.id} className="cursor-pointer hover:opacity-90 transition-opacity">
                <circle cx={node.x} cy={node.y} r={isSource || isSink ? "25" : "20"} fill={nodeColor} stroke="#fff" strokeWidth="3" />
                <text x={node.x} y={node.y} dy="45" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold">
                  {node.id}
                </text>
                {(isSource || isSink) && (
                  <text x={node.x} y={node.y} dy="5" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
                    {isSource ? "SRC" : "DST"}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

/* --- 2. RESOURCE MANAGER --- */
function ResourceManager({ notify }) {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newItem, setNewItem] = useState({ name: '', volume: 1, priority_score: 1, quantity: 1 });

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      const res = await fetch(`${API_BASE}/resources/`);
      if (res.ok) {
        setResources(await res.json());
      }
    } catch (e) {
      notify("Failed to load resources", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/resources/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItem)
      });
      if (res.ok) {
        notify("Resource added!");
        setNewItem({ name: '', volume: 1, priority_score: 1, quantity: 1 });
        fetchResources();
      } else {
        notify("Failed to add resource", "error");
      }
    } catch (e) { notify("Error adding resource", "error"); }
  };

  const handleDelete = async (id) => {
    if(!window.confirm("Delete this resource?")) return;
    try {
      const res = await fetch(`${API_BASE}/resources/${id}/`, { method: 'DELETE' });
      if (res.ok) {
        notify("Resource deleted");
        fetchResources();
      }
    } catch (e) { notify("Error deleting", "error"); }
  };

  const handleCsvSuccess = () => {
    fetchResources();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {/* Sidebar: Add Form & CSV Upload */}
      <div className="md:col-span-1 space-y-6">
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-5 h-5 text-emerald-600" /> Add Resource
          </h3>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase">Item Name</label>
              <input 
                type="text" 
                value={newItem.name}
                onChange={e => setNewItem({...newItem, name: e.target.value})}
                className="w-full p-2 border border-slate-300 rounded focus:border-emerald-500 focus:outline-none"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase">Volume</label>
                <input 
                  type="number" min="1"
                  value={newItem.volume}
                  onChange={e => setNewItem({...newItem, volume: parseInt(e.target.value)})}
                  className="w-full p-2 border border-slate-300 rounded focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase">Priority</label>
                <input 
                  type="number" min="1"
                  value={newItem.priority_score}
                  onChange={e => setNewItem({...newItem, priority_score: parseInt(e.target.value)})}
                  className="w-full p-2 border border-slate-300 rounded focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-bold text-slate-500 uppercase">Quantity</label>
              <input 
                type="number" min="1"
                value={newItem.quantity}
                onChange={e => setNewItem({...newItem, quantity: parseInt(e.target.value)})}
                className="w-full p-2 border border-slate-300 rounded focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <button type="submit" className="w-full py-2 bg-emerald-600 text-white rounded-lg font-bold hover:bg-emerald-700 transition-colors">
              Add Item
            </button>
          </form>
        </div>

        <ResourceCsvWidget onUploadSuccess={handleCsvSuccess} notify={notify} />

      </div>

      {/* List */}
      <div className="md:col-span-2">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200 font-bold text-slate-700">
            Available Inventory
          </div>
          <div className="max-h-[600px] overflow-y-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 sticky top-0">
                <tr>
                  <th className="p-4">Name</th>
                  <th className="p-4 text-center">Vol</th>
                  <th className="p-4 text-center">Priority</th>
                  <th className="p-4 text-center">Qty</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {resources.map(r => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="p-4 font-medium">{r.name}</td>
                    <td className="p-4 text-center">{r.volume}</td>
                    <td className="p-4 text-center text-emerald-600 font-bold">{r.priority_score}</td>
                    <td className="p-4 text-center">{r.quantity}</td>
                    <td className="p-4 text-right">
                      <button onClick={() => handleDelete(r.id)} className="text-rose-500 hover:bg-rose-50 p-2 rounded">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {resources.length === 0 && (
                  <tr><td colSpan="5" className="p-8 text-center text-slate-400">No resources added yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResourceCsvWidget({ onUploadSuccess, notify }) {
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/upload/resources/`, {
        method: 'POST',
        body: formData,
      });
      
      // Handle HTML 404/500 responses gracefully
      if (res.status === 404) {
        throw new Error("API Endpoint Not Found. Did you update the backend urls.py?");
      }
      
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (jsonErr) {
        throw new Error("Server returned non-JSON response. Check backend logs.");
      }
      
      if (res.ok && data.success) {
        onUploadSuccess();
        notify(data.message || "Resources uploaded successfully!");
      } else {
        notify(data.message || "Upload failed: Invalid Format?", 'error');
      }
    } catch (err) {
      console.error("Resource Upload Error:", err);
      notify(err.message, 'error');
    } finally {
      setUploading(false);
      e.target.value = null; // Reset input
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
      <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-blue-600" /> Bulk Upload
      </h3>
      <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center hover:bg-slate-50 transition-colors relative group">
        <input 
          type="file" 
          accept=".csv"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        <Upload className={`w-8 h-8 text-slate-300 mx-auto mb-2 group-hover:text-blue-500 transition-colors ${uploading ? 'animate-bounce' : ''}`} />
        <p className="text-sm text-slate-600 font-medium">
          {uploading ? 'Uploading...' : 'Upload CSV File'}
        </p>
        <p className="text-xs text-slate-400 mt-1">Format: Name, Vol, Score, Qty</p>
      </div>
    </div>
  );
}

/* --- 3. EXISTING COMPONENTS (Preserved) --- */

function DataManager({ notify, refreshStatus }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editItem, setEditItem] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false); // New State
  const [newItem, setNewItem] = useState({ A: '', to: '', max_capacity: 0 }); // New Item State

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/flows/`);
      if (res.ok) { setRows(await res.json()); }
    } catch (e) { notify("Error fetching data", "error"); } finally { setLoading(false); }
  };

  const handleDelete = async (id) => {
    if(!window.confirm("Delete route?")) return;
    try {
      const res = await fetch(`${API_BASE}/flows/${id}/`, { method: 'DELETE' });
      if (res.ok) { notify("Deleted"); fetchData(); refreshStatus(); }
    } catch(e) { notify("Error deleting", "error"); }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/flows/${editItem.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editItem)
      });
      if (res.ok) { notify("Updated"); setEditItem(null); fetchData(); }
    } catch(e) { notify("Error updating", "error"); }
  };

  // --- NEW: Add Route Logic ---
  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/flows/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItem)
      });
      if (res.ok) { 
        notify("New route added successfully!"); 
        setIsAddModalOpen(false); 
        setNewItem({ A: '', to: '', max_capacity: 0 }); // Reset form
        fetchData(); 
        refreshStatus();
      } else {
        notify("Failed to create route", "error");
      }
    } catch(e) { notify("Error creating route", "error"); }
  };

  return (
    <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden animate-fade-in">
      <div className="bg-slate-50 p-6 border-b border-slate-200 flex justify-between items-center">
        <h3 className="text-xl font-bold text-slate-800">Transport Network Data</h3>
        <div className="flex gap-2">
          {/* NEW ADD BUTTON */}
          <button 
            onClick={() => setIsAddModalOpen(true)} 
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-bold text-sm"
          >
            <Plus size={16} /> Add Route
          </button>
          <button onClick={fetchData} className="p-2 hover:bg-slate-200 rounded-full text-slate-500">
            <RefreshCw size={18}/>
          </button>
        </div>
      </div>

      <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0">
            <tr>
              <th className="p-4 font-bold">Source</th>
              <th className="p-4 font-bold">Destination</th>
              <th className="p-4 font-bold text-right">Capacity</th>
              <th className="p-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map(row => (
              <tr key={row.id} className="hover:bg-slate-50">
                <td className="p-4 font-medium">{row.A}</td>
                <td className="p-4 text-slate-600">{row.to}</td>
                <td className="p-4 text-right font-mono font-bold text-emerald-600">{row.max_capacity}</td>
                <td className="p-4 text-center flex justify-center gap-2">
                  <button onClick={() => setEditItem(row)} className="p-2 text-blue-600 hover:bg-blue-50 rounded"><Pencil size={16}/></button>
                  <button onClick={() => handleDelete(row.id)} className="p-2 text-rose-500 hover:bg-rose-50 rounded"><Trash2 size={16}/></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* NEW: Add Route Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100]">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md animate-fade-in-up shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-slate-800">Add New Transport Route</h3>
              <button onClick={() => setIsAddModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={24} />
              </button>
            </div>
            <form onSubmit={handleAdd} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Source District</label>
                <input 
                  type="text" 
                  value={newItem.A} 
                  onChange={e=>setNewItem({...newItem, A:e.target.value})} 
                  className="w-full p-3 border border-slate-300 rounded-lg focus:border-emerald-500 focus:outline-none" 
                  placeholder="e.g. Dhaka"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Destination District</label>
                <input 
                  type="text" 
                  value={newItem.to} 
                  onChange={e=>setNewItem({...newItem, to:e.target.value})} 
                  className="w-full p-3 border border-slate-300 rounded-lg focus:border-emerald-500 focus:outline-none" 
                  placeholder="e.g. Comilla"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Max Capacity</label>
                <input 
                  type="number" 
                  min="1"
                  value={newItem.max_capacity} 
                  onChange={e=>setNewItem({...newItem, max_capacity:parseInt(e.target.value)})} 
                  className="w-full p-3 border border-slate-300 rounded-lg focus:border-emerald-500 focus:outline-none" 
                  placeholder="e.g. 500"
                  required
                />
              </div>
              <button type="submit" className="w-full py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 shadow-md transition-all flex justify-center items-center gap-2">
                <Plus size={18} /> Create Route
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal (Existing) */}
      {editItem && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100]">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md animate-fade-in-up">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-slate-800">Edit Route</h3>
              <button onClick={() => setEditItem(null)} className="text-slate-400 hover:text-slate-600"><X size={24} /></button>
            </div>
            <form onSubmit={handleUpdate} className="space-y-4">
              <input type="text" value={editItem.A} onChange={e=>setEditItem({...editItem, A:e.target.value})} className="w-full p-3 border rounded-lg" placeholder="Source"/>
              <input type="text" value={editItem.to} onChange={e=>setEditItem({...editItem, to:e.target.value})} className="w-full p-3 border rounded-lg" placeholder="Destination"/>
              <input type="number" value={editItem.max_capacity} onChange={e=>setEditItem({...editItem, max_capacity:e.target.value})} className="w-full p-3 border rounded-lg" placeholder="Capacity"/>
              <div className="flex gap-2">
                <button type="button" onClick={()=>setEditItem(null)} className="flex-1 py-3 bg-slate-100 rounded-lg font-bold text-slate-600">Cancel</button>
                <button type="submit" className="flex-1 py-3 bg-emerald-600 text-white rounded-lg font-bold">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function CsvUploader({ onUploadSuccess, notify }) {
  const [uploading, setUploading] = useState(false);
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/upload/`, { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok && data.success) onUploadSuccess();
      else notify(data.message || "Upload failed", 'error');
    } catch (err) { notify("Connection error", 'error'); } 
    finally { setUploading(false); e.target.value = null; }
  };
  return (
    <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100 max-w-4xl mx-auto p-12 text-center">
      <div className="border-4 border-dashed border-slate-200 rounded-3xl p-12 bg-slate-50 hover:bg-emerald-50 transition-colors relative">
        <input type="file" accept=".csv" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer" disabled={uploading}/>
        <Upload className={`w-16 h-16 text-slate-300 mx-auto mb-4 ${uploading?'animate-bounce text-emerald-500':''}`}/>
        <h2 className="text-2xl font-bold text-slate-700">{uploading ? 'Uploading...' : 'Upload Network CSV'}</h2>
        <p className="text-slate-500 mt-2">Format: Source, Destination, Capacity</p>
      </div>
    </div>
  );
}

function FlowCalculator({ notify, result, setResult, allocation, setAllocation }) {
  const [source, setSource] = useState('');
  const [sink, setSink] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true); setResult(null); setAllocation(null);
    try {
      const res = await fetch(`${API_BASE}/calculate-flow/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, sink })
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
        const allocRes = await fetch(`${API_BASE}/calculate-knapsack/`);
        if (allocRes.ok) setAllocation(await allocRes.json());
      } else { notify(data.error || "Error", 'error'); }
    } catch (err) { notify("Connection failed", 'error'); } 
    finally { setLoading(false); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div className="lg:col-span-4 space-y-6">
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 sticky top-24">
          <h2 className="text-2xl font-bold flex items-center gap-2 mb-6"><Search className="text-emerald-600"/> Calculator</h2>
          <form onSubmit={handleCalculate} className="space-y-4">
            <input type="text" placeholder="Source (e.g. Dhaka)" value={source} onChange={e=>setSource(e.target.value)} className="w-full p-4 border-2 border-slate-200 rounded-xl" required/>
            <input type="text" placeholder="Dest (e.g. Chittagong)" value={sink} onChange={e=>setSink(e.target.value)} className="w-full p-4 border-2 border-slate-200 rounded-xl" required/>
            <button disabled={loading} className="w-full py-4 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 disabled:opacity-50">
              {loading ? 'Calculating...' : 'Run Optimization'}
            </button>
          </form>
          {result && (
             <div className="mt-8 bg-slate-900 text-white p-6 rounded-2xl text-center">
               <div className="text-xs uppercase font-bold text-emerald-400 mb-2">Max Throughput</div>
               <div className="text-5xl font-extrabold">{result.max_flow}</div>
             </div>
          )}
        </div>
      </div>
      <div className="lg:col-span-8 space-y-8">
        {result && (
          <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
             <div className="bg-slate-50 p-6 border-b border-slate-200 font-bold">Flow Distribution</div>
             <table className="w-full text-left text-sm">
               <thead className="bg-slate-50 text-slate-500 border-b"><tr><th className="p-4">From</th><th className="p-4">To</th><th className="p-4 text-right">Flow</th></tr></thead>
               <tbody>
                 {Object.entries(result.details).flatMap(([u, n]) => Object.entries(n).map(([v, f]) => (
                   <tr key={u+v}><td className="p-4 font-bold">{u}</td><td className="p-4">{v}</td><td className="p-4 text-right font-mono text-emerald-600 font-bold">{f}</td></tr>
                 )))}
               </tbody>
             </table>
          </div>
        )}
        {allocation && Object.keys(allocation).length > 0 && (
          <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
             <div className="bg-indigo-50 p-6 border-b border-indigo-100 font-bold text-indigo-900">Resource Allocation</div>
             <div className="p-6 grid gap-4">
                {Object.entries(allocation).map(([k, d]) => (
                  <div key={k} className="border p-4 rounded-xl">
                    <div className="flex justify-between font-bold mb-2"><span>{d.source} → {d.destination}</span><span className="text-xs bg-slate-100 px-2 py-1 rounded">Cap: {d.capacity}</span></div>
                    <div className="flex flex-wrap gap-2">
                      {d.items.length ? d.items.map((i,x)=><span key={x} className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-xs font-bold">{i.name}</span>) : <span className="text-slate-400 italic text-sm">No items fit</span>}
                    </div>
                  </div>
                ))}
             </div>
          </div>
        )}
      </div>
    </div>
  );
}