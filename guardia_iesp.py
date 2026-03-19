import React, { useState, useEffect } from 'react';
import { 
  Shield, Users, FileText, Settings, LogOut, 
  ChevronRight, Search, Plus, Trash2, Download, 
  RefreshCw, CheckCircle, AlertCircle, Clock, 
  UserCheck, ShieldAlert, LayoutDashboard
} from 'lucide-react';

/**
 * SISTEMA DE GESTIÓN DE GUARDIA IESP - VERSIÓN PRO 2026
 * Diseño de vanguardia con React + Tailwind CSS
 */

const App = () => {
  // --- ESTADOS ---
  const [isLogged, setIsLogged] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Datos de ejemplo simulando base de datos
  const [groups, setGroups] = useState([
    { id: 1, name: "Guardia 1 de III° Año", status: "De Servicio", chief: "Juarez Ignacio" },
    { id: 2, name: "Guardia 2 de III° Año", status: "Franco", chief: "Mercado Marcelo" },
    { id: 3, name: "Guardia 1 de II° Año", status: "Instrucción", chief: "Forales Emanuel" }
  ]);

  const [cadetes, setCadetes] = useState([
    { id: 1, nombre: "Juarez Ignacio", curso: "IIIº Año", funcion: "Jefe de Guardia", situacion: "PRESENTE", group: 1 },
    { id: 2, nombre: "Contreras Melani", curso: "IIIº Año", funcion: "Cabo de Cuarto", situacion: "PRESENTE", group: 1 },
    { id: 3, nombre: "Bareiro Blanca", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "PRESENTE", group: 1 },
    { id: 4, nombre: "Etchenique Shamira", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "FRANCO", group: 1 },
    { id: 5, nombre: "Abregu Franco", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "PRESENTE", group: 1 },
    { id: 6, nombre: "Aguirre Santiago", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "A.R.T.", group: 1 },
    { id: 7, nombre: "Arias Ramiro", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "PRESENTE", group: 1 },
    { id: 8, nombre: "Arganaraz Roberto", curso: "IIº Año", funcion: "Cadete Apostado", situacion: "PRESENTE", group: 1 },
  ]);

  const [castigos, setCastigos] = useState([
    { id: 101, nombre: "Pérez Juan", curso: "IIº Año", motivo: "Llegada Tarde" }
  ]);

  // --- LÓGICA ---
  const handleLogin = (e) => {
    e.preventDefault();
    const pwd = e.target.password.value;
    if (pwd === "iesp2026") setIsLogged(true);
  };

  const updateSituacion = (id, sit) => {
    setCadetes(cadetes.map(c => c.id === id ? { ...c, situacion: sit } : c));
  };

  // --- COMPONENTES DE INTERFAZ ---

  if (!isLogged) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-4 relative overflow-hidden">
        {/* Decoración de fondo */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-red-600/10 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full"></div>
        
        <div className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-10 rounded-[32px] shadow-2xl z-10 text-center">
          <div className="inline-flex p-4 bg-gradient-to-tr from-red-500 to-red-600 rounded-2xl shadow-lg shadow-red-500/20 mb-6">
            <Shield className="text-white w-10 h-10" />
          </div>
          <h1 className="text-3xl font-black text-white tracking-tighter mb-2 uppercase">IESP GUARDIA</h1>
          <p className="text-slate-400 text-sm mb-10 font-medium">Plataforma de Diagramación Avanzada 2026</p>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="relative group text-left">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-4 mb-2 block">Contraseña de Acceso</label>
              <input 
                name="password"
                type="password" 
                placeholder="••••••••" 
                className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-white outline-none focus:border-red-500/50 focus:ring-4 focus:ring-red-500/10 transition-all text-center font-mono tracking-widest"
              />
            </div>
            <button className="w-full bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white font-bold py-4 rounded-2xl shadow-xl shadow-red-600/20 transition-all transform hover:scale-[1.02] active:scale-[0.98] uppercase text-xs tracking-[0.2em]">
              Entrar al Sistema
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] flex font-sans text-slate-900">
      {/* Sidebar Lateral */}
      <aside className="w-72 bg-[#0f172a] text-white flex flex-col shadow-2xl fixed h-screen z-30">
        <div className="p-8 flex items-center gap-3 border-b border-white/5">
          <div className="bg-red-600 p-2 rounded-lg">
            <Shield size={20} />
          </div>
          <span className="font-black tracking-tighter uppercase text-lg">IESP <span className="text-red-500 font-light">Pro</span></span>
        </div>
        
        <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
            { id: 'groups', icon: Users, label: 'Todas las Guardias' },
            { id: 'punishment', icon: ShieldAlert, label: 'Guardia Castigo' },
            { id: 'reports', icon: FileText, label: 'Reportes PDF' },
            { id: 'settings', icon: Settings, label: 'Ajustes de Ciclo' },
          ].map(item => (
            <button 
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-4 p-4 rounded-2xl text-sm font-bold transition-all ${activeTab === item.id ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
            >
              <item.icon size={18} /> {item.label}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/5">
          <button 
            onClick={() => setIsLogged(false)}
            className="w-full flex items-center gap-4 p-4 rounded-2xl text-sm font-bold text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut size={18} /> Salir
          </button>
        </div>
      </aside>

      {/* Contenido Principal */}
      <main className="flex-1 ml-72 p-10 bg-gradient-to-b from-white to-[#f1f5f9] min-h-screen">
        {/* Top Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-black text-[#0f172a] tracking-tighter uppercase">Diagramación de Guardia</h2>
            <div className="flex items-center gap-2 text-slate-400 text-sm mt-1">
              <Clock size={14} /> <span>Viernes, 19 de Marzo de 2026</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="Buscar cadete..." 
                className="bg-white border border-slate-200 rounded-full pl-12 pr-6 py-3 text-sm focus:ring-4 focus:ring-red-500/5 outline-none w-64 transition-all focus:w-80"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest border border-green-200 animate-pulse">
              Servidor Activo
            </div>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Sincronización */}
            <div className="bg-[#0f172a] p-1 rounded-[32px] flex">
              <button className="flex-1 bg-white/5 hover:bg-white/10 text-white text-xs font-black uppercase tracking-widest py-4 rounded-[28px] transition-all flex items-center justify-center gap-3">
                <RefreshCw size={14} className="text-red-500" /> Recalibrar Ciclo Operativo
              </button>
            </div>

            {/* Métricas */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { label: "Grupo en Turno", val: "N° 1 IIIº Año", color: "blue", icon: UserCheck },
                { label: "Efectivos Hoy", val: "13 Cadetes", color: "green", icon: Users },
                { label: "Novedades ART", val: "02 Casos", color: "red", icon: ShieldAlert },
                { label: "Suplencias", val: "01 Activa", color: "amber", icon: RefreshCw },
              ].map((m, i) => (
                <div key={i} className="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm hover:shadow-xl transition-all group">
                  <div className={`w-10 h-10 rounded-xl mb-4 flex items-center justify-center bg-${m.color}-50 text-${m.color}-600 group-hover:scale-110 transition-transform`}>
                    <m.icon size={20} />
                  </div>
                  <p className="text-slate-400 text-[10px] font-black uppercase tracking-widest mb-1">{m.label}</p>
                  <h3 className="text-xl font-black text-[#0f172a]">{m.val}</h3>
                </div>
              ))}
            </div>

            {/* Tabla Principal */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="bg-white rounded-[40px] border border-slate-100 shadow-sm overflow-hidden">
                  <div className="p-8 border-b border-slate-50 flex justify-between items-center bg-white">
                    <h3 className="font-black text-lg text-[#0f172a] uppercase tracking-tighter flex items-center gap-3">
                      <Users size={20} className="text-red-500" /> Nómina del Personal
                    </h3>
                    <input 
                      type="date" 
                      className="bg-slate-50 border-none rounded-xl px-4 py-2 text-xs font-bold" 
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                    />
                  </div>
                  <div className="p-2">
                    <table className="w-full">
                      <thead>
                        <tr className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em]">
                          <th className="px-6 py-4 text-left">Orden</th>
                          <th className="px-6 py-4 text-left">Apellido y Nombre</th>
                          <th className="px-6 py-4 text-left">Función</th>
                          <th className="px-6 py-4 text-left">Estado</th>
                          <th className="px-6 py-4 text-right">Ajuste</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {cadetes.map((c, i) => (
                          <tr key={i} className="hover:bg-slate-50/50 transition-colors group">
                            <td className="px-6 py-5 text-sm font-bold text-slate-300">#{c.id}</td>
                            <td className="px-6 py-5">
                              <p className="text-sm font-black text-[#0f172a] uppercase">{c.nombre}</p>
                              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{c.curso}</p>
                            </td>
                            <td className="px-6 py-5">
                              <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-lg text-[9px] font-black uppercase">
                                {c.funcion}
                              </span>
                            </td>
                            <td className="px-6 py-5">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${c.situacion === 'PRESENTE' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <span className={`text-[10px] font-black uppercase ${c.situacion === 'PRESENTE' ? 'text-green-600' : 'text-red-600'}`}>
                                  {c.situacion}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-5 text-right">
                              <button className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all">
                                <Settings size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Acciones Rápidas Derecha */}
              <div className="space-y-6">
                <div className="bg-white p-8 rounded-[40px] border border-slate-100 shadow-sm">
                  <h4 className="font-black text-sm uppercase tracking-widest text-slate-400 mb-6">Gestión de Estados</h4>
                  <div className="space-y-4">
                    <button className="w-full flex items-center justify-between p-4 bg-slate-50 rounded-2xl hover:bg-slate-100 transition-all border border-transparent hover:border-slate-200 group">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white rounded-lg group-hover:bg-red-500 group-hover:text-white transition-all shadow-sm">
                          <Plus size={16} />
                        </div>
                        <span className="text-xs font-black uppercase">Marcar Novedad</span>
                      </div>
                      <ChevronRight size={14} className="text-slate-300" />
                    </button>
                    <button className="w-full flex items-center justify-between p-4 bg-slate-50 rounded-2xl hover:bg-slate-100 transition-all border border-transparent hover:border-slate-200 group">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white rounded-lg group-hover:bg-blue-500 group-hover:text-white transition-all shadow-sm">
                          <RefreshCw size={16} />
                        </div>
                        <span className="text-xs font-black uppercase">Asignar Suplente</span>
                      </div>
                      <ChevronRight size={14} className="text-slate-300" />
                    </button>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-red-600 to-red-500 p-8 rounded-[40px] shadow-xl shadow-red-600/20 text-white">
                  <h4 className="font-black text-sm uppercase tracking-widest mb-6 opacity-80">Guardia Castigo</h4>
                  <div className="space-y-4 mb-6">
                    {castigos.map((p, i) => (
                      <div key={i} className="flex justify-between items-center bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/10">
                        <div>
                          <p className="text-xs font-black uppercase">{p.nombre}</p>
                          <p className="text-[9px] font-bold opacity-60 uppercase">{p.curso}</p>
                        </div>
                        <Trash2 size={14} className="cursor-pointer hover:text-red-200 transition-colors" />
                      </div>
                    ))}
                  </div>
                  <button className="w-full bg-white text-red-600 font-black text-[10px] uppercase tracking-[0.2em] py-4 rounded-2xl hover:bg-red-50 transition-all">
                    Agregar Refuerzo
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'groups' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-in zoom-in-95 duration-500">
            {groups.map((g, i) => (
              <div key={i} className="bg-white rounded-[40px] border border-slate-100 p-8 shadow-sm hover:shadow-2xl transition-all hover:scale-[1.02] cursor-pointer group">
                <div className="flex justify-between items-start mb-8">
                  <div className="bg-slate-900 text-white w-12 h-12 rounded-2xl flex items-center justify-center font-black">
                    G{g.id}
                  </div>
                  <span className={`px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest ${g.status === 'De Servicio' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-400'}`}>
                    {g.status}
                  </span>
                </div>
                <h3 className="text-xl font-black text-[#0f172a] uppercase mb-1">{g.name}</h3>
                <p className="text-slate-400 text-xs font-bold mb-6 italic">Jefe: {g.chief}</p>
                <div className="space-y-3">
                  {[1,2,3].map(item => (
                    <div key={item} className="flex items-center gap-3 text-slate-600 text-[11px] font-bold uppercase tracking-tight opacity-70">
                      <CheckCircle size={12} className="text-green-500" /> Cadete de Ejemplo {item}
                    </div>
                  ))}
                  <p className="text-center text-[9px] font-black text-slate-300 uppercase tracking-widest pt-4">Ver nómina completa</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="max-w-2xl mx-auto text-center py-20 bg-white rounded-[50px] border border-slate-100 shadow-sm animate-in fade-in duration-700">
            <div className="bg-slate-50 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8">
              <Download size={40} className="text-slate-300" />
            </div>
            <h3 className="text-3xl font-black text-[#0f172a] mb-4 tracking-tighter uppercase">Generador de Planillas</h3>
            <p className="text-slate-400 mb-10 max-w-sm mx-auto font-medium">Seleccione el rango de fechas para exportar los diagramas oficiales listos para firma y archivo.</p>
            
            <div className="flex gap-4 justify-center mb-10">
              <input type="date" className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-bold outline-none" />
              <input type="date" className="bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-bold outline-none" />
            </div>

            <button className="bg-[#0f172a] text-white px-10 py-5 rounded-[24px] font-black text-xs uppercase tracking-[0.3em] hover:bg-red-600 transition-all shadow-xl shadow-slate-900/10 active:scale-95">
              Generar Lote PDF
            </button>
          </div>
        )}
      </main>

      {/* Marca de agua / Créditos */}
      <footer className="fixed bottom-8 right-12 pointer-events-none">
        <p className="text-[10px] font-black text-slate-300 uppercase tracking-[0.4em]">IESP SYSTEM SINC © 2026</p>
      </footer>
    </div>
  );
};

export default App;
