"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { productAPI } from '@/lib/api';
import { Search, Loader2, LogOut, CheckCircle2, TrendingUp, Grid3X3, Plus } from 'lucide-react';
import ProductCard from '@/components/ProductCard';
import PriceSheet from '@/components/PriceSheet';

export default function DashboardPage() {
    const { user, logout, loading } = useAuth();
    const [query, setQuery] = useState('');
    const [searching, setSearching] = useState(false);
    const [results, setResults] = useState<any[]>([]);
    const [searchError, setSearchError] = useState('');
    const [stats, setStats] = useState<any>(null);
    const [activeSheet, setActiveSheet] = useState<any>(null);
    const [generatingSheet, setGeneratingSheet] = useState(false);
    const [brandSearch, setBrandSearch] = useState(false);

    useEffect(() => {
        if (user) {
            productAPI.getDashboard().then(res => setStats(res.data)).catch(console.error);
        }
    }, [user]);

    if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>;
    if (!user) {
        if (typeof window !== 'undefined') window.location.href = '/login';
        return null;
    }

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        const trimmedQuery = query.trim();
        if (!trimmedQuery) return;

        if (brandSearch) {
            handleGenerateSheet();
            return;
        }

        setSearching(true);
        setSearchError('');
        setResults([]);
        setActiveSheet(null);
        try {
            const res = await productAPI.search(trimmedQuery);
            setResults(res.data.results);
            // refresh stats
            const stRes = await productAPI.getDashboard();
            setStats(stRes.data);
        } catch (err: any) {
            setSearchError(err.response?.data?.detail || 'Search failed. Please try again.');
        } finally {
            setSearching(false);
        }
    };

    const handleGenerateSheet = async () => {
        setGeneratingSheet(true);
        setSearchError('');
        setResults([]);
        try {
            if (brandSearch && query.trim()) {
                const res = await productAPI.generateSheet(`${query.toUpperCase()} BRAND SHEET`, [], true, query);
                setActiveSheet(res.data);
            } else {
                // Default models for demonstration
                const defaultModels = [
                    "iPhone 13 128", "iPhone 13 256", "iPhone 14 128", "iPhone 14 256",
                    "iPhone 15 128", "iPhone 15 256", "iPhone 16 128", "iPhone 16 256",
                    "iPhone 16e 128", "iPhone 17 256", "iPhone 17 Pro 256", "iPhone 17 Pro Max 256",
                    "AirPod 4th Gen", "AirPod Pro 2nd Gen", "iPad 11th Gen 128 WiFi"
                ];
                const res = await productAPI.generateSheet("GENERAL PRICE SHEET", defaultModels);
                setActiveSheet(res.data);
            }
        } catch (err: any) {
            setSearchError("Failed to generate AI sheet: " + (err.response?.data?.detail || "Unknown error"));
        } finally {
            setGeneratingSheet(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Top Navbar */}
            <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-blue-500" />
                        <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">PriceIntel</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-sm text-slate-400 hidden sm:block">
                            {user.email} <span className="ml-2 uppercase text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full">{user.role}</span>
                        </div>
                        <button onClick={logout} className="text-slate-400 hover:text-white transition-colors">
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </header>

            <main className="flex-1 container mx-auto px-4 py-8">
                {/* Dashboard Stats */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
                        <div className="glass-panel p-4 flex items-center gap-4">
                            <div className="p-3 bg-blue-500/10 rounded-lg"><Search className="w-6 h-6 text-blue-400" /></div>
                            <div><p className="text-2xl font-bold">{stats.total_searches}</p><p className="text-xs text-slate-400">Total Searches</p></div>
                        </div>
                        <div className="glass-panel p-4 flex items-center gap-4">
                            <div className="p-3 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="w-6 h-6 text-emerald-400" /></div>
                            <div><p className="text-2xl font-bold">{stats.searches_today}</p><p className="text-xs text-slate-400">Searches Today</p></div>
                        </div>
                        <div className="glass-panel p-4 flex items-center gap-4">
                            <div className="p-3 bg-rose-500/10 rounded-lg"><div className="w-6 h-6 text-rose-400" /></div>
                            <div><p className="text-2xl font-bold">{stats.saved_alerts}</p><p className="text-xs text-slate-400">Active Alerts</p></div>
                        </div>
                        <div className="glass-panel p-4 flex items-center gap-4">
                            <div className="p-3 bg-purple-500/10 rounded-lg"><TrendingUp className="w-6 h-6 text-purple-400" /></div>
                            <div><p className="text-2xl font-bold uppercase">{stats.plan}</p><p className="text-xs text-slate-400">Current Plan</p></div>
                        </div>
                    </div>
                )}

                {/* Search Bar */}
                <div className="max-w-2xl mx-auto mb-12 text-center space-y-6">
                    <h1 className="text-3xl md:text-5xl font-bold tracking-tight">Compare Prices Globally</h1>
                    <p className="text-slate-400">Enter a product name to search across Amazon and Flipkart simultaneously.</p>
                    <form onSubmit={handleSearch} className="relative mt-8 group">
                        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                            <Search className="w-5 h-5 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
                        </div>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="w-full h-14 pl-12 pr-32 bg-slate-900 border border-slate-700 rounded-full text-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-xl text-white block placeholder:text-slate-500"
                            placeholder="e.g. iPhone 15 Pro Max 256GB"
                            required
                        />
                        <button
                            type="submit"
                            disabled={searching}
                            className="absolute right-2 top-2 bottom-2 px-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
                        >
                            {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
                        </button>
                    </form>
                    {searchError && <p className="text-red-400 text-sm mt-2">{searchError}</p>}

                    <div className="flex items-center justify-center gap-2 mt-4">
                        <input
                            type="checkbox"
                            id="brandSearch"
                            checked={brandSearch}
                            onChange={(e) => setBrandSearch(e.target.checked)}
                            className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="brandSearch" className="text-sm text-slate-400 cursor-pointer select-none">
                            Enable Brand Discovery (Fetch all products for this company)
                        </label>
                    </div>

                    <div className="flex justify-center gap-4 mt-8">
                        <button
                            onClick={() => { setResults([]); setActiveSheet(null); }}
                            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${!activeSheet && results.length === 0 ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400'}`}
                        >
                            Quick Search
                        </button>
                        <button
                            onClick={handleGenerateSheet}
                            disabled={generatingSheet}
                            className={`px-6 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${activeSheet ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                        >
                            {generatingSheet ? <Loader2 className="w-4 h-4 animate-spin" /> : <Grid3X3 className="w-4 h-4" />}
                            AI Price Sheet
                        </button>
                    </div>
                </div>

                {/* Results Area */}
                {(searching || generatingSheet) && (
                    <div className="py-20 text-center space-y-4 animate-pulse">
                        <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto" />
                        <p className="text-slate-400 text-lg">
                            {generatingSheet ? 'Generating full AI autofill price sheet...' : 'Scraping global markets for the best prices...'}
                        </p>
                    </div>
                )}

                {activeSheet && !generatingSheet && (
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                        <PriceSheet data={activeSheet} />
                    </div>
                )}

                {!searching && !generatingSheet && results.length > 0 && (
                    <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">
                        <div className="flex items-center justify-between mb-8">
                            <h2 className="text-2xl font-bold">Comparison Results</h2>
                            <span className="text-sm text-slate-400 px-3 py-1 bg-slate-800 rounded-full">{results.length} offers found</span>
                        </div>
                        {results.map((product, i) => (
                            <ProductCard key={product.id || i} product={product} />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
