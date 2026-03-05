"use client";

import React from 'react';

interface PriceSheetRow {
    id: number;
    model_name: string;
    channel: string;
    retailer?: string;
    mop_offline: number;
    cif_offline: number;
    mop_online: number;
    secure_packaging: number;
    offer_handling: number;
    corp_fees: number;
    coupon: number;
    bank_hdfc: number;
    bank_icici: number;
    swipe_amount: number;
    cashback_hdfc: number;
    cashback_icici: number;
    cashback_emi: number;
    landing_price: number;
    emi_landing: number;
    cif_cost_today: number;
    remark: string;
    product_url?: string;
}

interface PriceSheetPincode {
    id: number;
    model_name: string;
    pincode: string;
    city_name: string;
    availability: string;
    delivery_date: string;
    colors?: string;
}

interface PriceSheetProps {
    data: {
        id?: number;
        name: string;
        rows: PriceSheetRow[];
        pincodes: PriceSheetPincode[];
    };
}

const PriceSheet: React.FC<PriceSheetProps> = ({ data }) => {
    const [activeTab, setActiveTab] = React.useState<'main' | 'pincode'>('main');
    const [subTab, setSubTab] = React.useState<string>('All');

    const formatPrice = (price?: number) => {
        if (!price || price === 0) return "-";
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(price).replace('₹', '₹ ');
    };

    const formatUSD = (val?: number) => {
        if (!val || val === 0) return "$0";
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(val);
    };

    // Get unique city names for the pincode tab headers
    const cities = Array.from(new Set(data.pincodes?.map(p => `${p.city_name} (${p.pincode})`) || []));
    const modelNames = Array.from(new Set(data.rows.map(r => r.model_name)));

    const retailers = ["All", "Amazon India", "Flipkart", "Vijay Sales", "Jio Mart"];

    const filteredRows = React.useMemo(() => {
        if (subTab === 'All') return data.rows;
        return data.rows.filter(r => r.retailer === subTab);
    }, [data.rows, subTab]);

    return (
        <div className="w-full overflow-hidden glass-panel border border-slate-800 rounded-xl">
            {/* Tab Header */}
            <div className="p-4 border-b border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900/50 gap-4">
                <div className="flex items-center gap-4">
                    <h3 className="text-xl font-bold text-white mr-4">{data.name}</h3>
                    <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 shadow-inner">
                        <button
                            onClick={() => setActiveTab('main')}
                            className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab === 'main' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Main Sheet
                        </button>
                        <button
                            onClick={() => setActiveTab('pincode')}
                            className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab === 'pincode' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Pincode Availability
                        </button>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-xs text-blue-500 font-mono uppercase tracking-widest bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20 animate-pulse">
                        Live AI Autofill Active
                    </span>
                    <button
                        onClick={async () => {
                            try {
                                const response = await (await import('@/lib/api')).productAPI.exportSheet(data.id as number, subTab);
                                const url = window.URL.createObjectURL(new Blob([response.data]));
                                const link = document.createElement('a');
                                link.href = url;
                                link.setAttribute('download', `PriceSheet_${data.id}.xlsx`);
                                document.body.appendChild(link);
                                link.click();
                                link.remove();
                            } catch (err) {
                                console.error("Export failed", err);
                                alert("Failed to export sheet. Please try again.");
                            }
                        }}
                        className="flex items-center gap-2 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-full transition-colors shadow-lg shadow-emerald-900/20"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Export Excel
                    </button>
                </div>
            </div>

            {/* Retailer Sub-Tabs */}
            {activeTab === 'main' && (
                <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex items-center gap-2 overflow-x-auto no-scrollbar">
                    {retailers.map(r => (
                        <button
                            key={r}
                            onClick={() => setSubTab(r)}
                            className={`px-4 py-1 rounded-full text-[10px] font-bold whitespace-nowrap transition-all border ${subTab === r
                                ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                                : 'bg-slate-800/50 border-slate-700 text-slate-500 hover:border-slate-600'
                                }`}
                        >
                            {r}
                        </button>
                    ))}
                </div>
            )}

            {activeTab === 'main' ? (
                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full text-[11px] text-left border-collapse min-w-[1600px]">
                        <thead>
                            {/* Multi-level Headers */}
                            <tr className="bg-slate-950/80 text-center uppercase tracking-tighter font-bold border-b border-slate-700">
                                <th className="p-4 border-r border-slate-700 sticky left-0 bg-slate-950 z-20 min-w-[220px]" rowSpan={2}>Models</th>
                                <th className="p-3 border-r border-slate-700 min-w-[80px]" rowSpan={2}>Retailer</th>
                                <th className="p-3 border-r border-slate-700 min-w-[80px]" rowSpan={2}>Channel</th>
                                <th className="p-2 border-r border-slate-700 bg-amber-500/20 text-amber-400" colSpan={2}>M.O.P Offline</th>
                                <th className="p-2 border-r border-slate-700 bg-blue-500/20 text-blue-400" colSpan={4}>M.O.P Online</th>
                                <th className="p-2 border-r border-slate-700 bg-purple-500/20 text-purple-400" colSpan={3}>Bank / Card Offers</th>
                                <th className="p-3 border-r border-slate-700 bg-emerald-500/20 text-emerald-400 min-w-[100px]" rowSpan={2}>Swipe Amount</th>
                                <th className="p-2 border-r border-slate-700 bg-rose-500/20 text-rose-400" colSpan={3}>Cashback</th>
                                <th className="p-2 border-r border-slate-700 bg-indigo-600/30 text-indigo-400" colSpan={2}>Final</th>
                                <th className="p-3 border-r border-slate-700 min-w-[100px]" rowSpan={2}>Today CIF Cost</th>
                                <th className="p-3 border-r border-slate-700 min-w-[50px]" rowSpan={2}>Link</th>
                                <th className="p-3 min-w-[150px]" rowSpan={2}>Remark</th>
                            </tr>
                            <tr className="bg-slate-900/40 text-slate-500 border-b border-slate-800 text-[9px]">
                                <th className="p-2 border-r border-slate-800">OFFLINE</th>
                                <th className="p-2 border-r border-slate-800 text-amber-500/80">$91.20</th>
                                <th className="p-2 border-r border-slate-800">ONLINE</th>
                                <th className="p-2 border-r border-slate-800">SECURE PKG</th>
                                <th className="p-2 border-r border-slate-800">HANDLING</th>
                                <th className="p-2 border-r border-slate-800">CORP FEES</th>
                                <th className="p-2 border-r border-slate-800">COUPON</th>
                                <th className="p-2 border-r border-slate-800">HDFC</th>
                                <th className="p-2 border-r border-slate-800">ICICI</th>
                                <th className="p-2 border-r border-slate-800">HDFC</th>
                                <th className="p-2 border-r border-slate-800">ICICI</th>
                                <th className="p-2 border-r border-slate-800">EMI</th>
                                <th className="p-2 border-r border-slate-800 text-indigo-400 font-bold">LANDING</th>
                                <th className="p-2 border-r border-slate-800">EMI LAND</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {filteredRows.map((row, idx) => (
                                <tr key={idx} className="hover:bg-blue-500/5 transition-colors group border-b border-slate-800/30">
                                    <td className="p-3 border-r border-slate-800 font-bold text-slate-200 sticky left-0 bg-slate-900 group-hover:bg-slate-800/80 transition-colors z-10">
                                        {row.model_name}
                                    </td>
                                    <td className="p-3 border-r border-slate-800 text-slate-400 text-center">
                                        <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${row.retailer?.includes('Amazon') ? 'bg-amber-500/10 border-amber-500/30 text-amber-500' :
                                            row.retailer?.includes('Flipkart') ? 'bg-blue-500/10 border-blue-500/30 text-blue-500' :
                                                row.retailer?.includes('Vijay') ? 'bg-rose-500/10 border-rose-500/30 text-rose-500' :
                                                    'bg-slate-500/10 border-slate-500/30 text-slate-400'
                                            }`}>
                                            {row.retailer || '-'}
                                        </span>
                                    </td>
                                    <td className="p-3 border-r border-slate-800 text-slate-400 text-center">{row.channel}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-slate-500">{formatPrice(row.mop_offline)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-slate-600 bg-amber-500/5">{formatUSD(row.cif_offline)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center font-bold text-white bg-blue-500/5">{formatPrice(row.mop_online)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-slate-500">{formatPrice(row.secure_packaging)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-slate-500">{formatPrice(row.offer_handling)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-slate-500">{formatPrice(row.corp_fees)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-purple-400">{formatPrice(row.coupon)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-purple-400">{formatPrice(row.bank_hdfc)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-purple-400">{formatPrice(row.bank_icici)}</td>
                                    <td className="p-3 border-r border-slate-800 text-center font-bold bg-emerald-500/10 text-emerald-400 shadow-inner">{formatPrice(row.swipe_amount)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-rose-500 bg-rose-500/5 font-medium">-{formatPrice(row.cashback_hdfc)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-rose-500 font-medium">-{formatPrice(row.cashback_icici)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center text-rose-500 font-medium">-{formatPrice(row.cashback_emi)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center font-black bg-indigo-600/20 text-indigo-400 text-xs shadow-lg ring-1 ring-inset ring-indigo-500/20">{formatPrice(row.landing_price)}</td>
                                    <td className="p-2 border-r border-slate-800 text-center font-bold text-slate-500">{formatPrice(row.emi_landing)}</td>
                                    <td className="p-3 border-r border-slate-800 text-center font-black text-purple-500 bg-purple-500/10 text-[13px]">{formatUSD(row.cif_cost_today)}</td>
                                    <td className="p-3 border-r border-slate-800 text-center">
                                        {row.product_url ? (
                                            <a href={row.product_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-400 transition-colors">
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                </svg>
                                            </a>
                                        ) : "-"}
                                    </td>
                                    <td className="p-3">
                                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest ${row.remark?.includes('OOS') ? 'bg-rose-500/20 text-rose-500' : 'bg-slate-700/50 text-slate-400'
                                            }`}>
                                            {row.remark || 'UPDATED'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                /* Pincode Tab Content */
                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full text-[11px] text-left border-collapse min-w-[2000px]">
                        <thead>
                            <tr className="bg-slate-950/80 text-center uppercase tracking-tighter font-bold border-b border-slate-700">
                                <th className="p-4 border-r border-slate-700 sticky left-0 bg-slate-950 z-20 min-w-[220px]">Models</th>
                                {cities.map(city => (
                                    <th key={city} className="p-3 border-r border-slate-700 bg-purple-500/10 text-purple-400 min-w-[150px]">{city}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {modelNames.map(model => (
                                <tr key={model} className="hover:bg-purple-500/5 transition-colors group border-b border-slate-800/30">
                                    <td className="p-3 border-r border-slate-800 font-bold text-slate-200 sticky left-0 bg-slate-900 group-hover:bg-slate-800/80 transition-colors z-10">
                                        {model}
                                    </td>
                                    {cities.map(city => {
                                        const cityData = data.pincodes.find(p => p.model_name === model && `${p.city_name} (${p.pincode})` === city);
                                        const isOOS = cityData?.availability === "OOS";
                                        return (
                                            <td key={city} className="p-3 border-r border-slate-800 text-center">
                                                {cityData ? (
                                                    <div className="flex flex-col items-center">
                                                        <span className={`text-[9px] font-bold uppercase tracking-widest ${isOOS ? 'text-rose-500' : 'text-emerald-500'}`}>
                                                            {cityData.availability}
                                                        </span>
                                                        <span className="text-[11px] text-slate-400 mt-0.5">
                                                            {cityData.delivery_date}
                                                        </span>
                                                        {cityData.colors && (
                                                            <span className="text-[9px] text-blue-400/80 mt-1 italic">
                                                                {cityData.colors}
                                                            </span>
                                                        )}
                                                    </div>
                                                ) : "-"}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <style jsx>{`
                .custom-scrollbar::-webkit-scrollbar {
                    height: 8px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: #020617;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #1e293b;
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #334155;
                }
            `}</style>
        </div>
    );
};

export default PriceSheet;
