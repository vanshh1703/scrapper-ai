import { ExternalLink, ShoppingCart, Star } from 'lucide-react';

export default function ProductCard({ product }: { product: any }) {
    const isCheapest = product.cheapest;
    const savings = product.savings_percent;

    const decisionColor = {
        'BUY NOW': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
        'WAIT': 'bg-rose-500/20 text-rose-400 border-rose-500/50',
        'GOOD PRICE': 'bg-blue-500/20 text-blue-400 border-blue-500/50',
        'UNKNOWN': 'bg-slate-500/20 text-slate-400 border-slate-500/50'
    }[product.decision as string] || 'bg-slate-500/20 text-slate-400 border-slate-500/50';

    return (
        <div className={`glass-panel overflow-hidden transition-all duration-300 ${isCheapest ? 'ring-2 ring-emerald-500 shadow-emerald-500/20 scale-[1.02]' : 'hover:border-slate-700'}`}>
            {isCheapest && (
                <div className="bg-emerald-500/10 text-emerald-400 text-xs font-bold px-4 py-1 flex items-center justify-between border-b border-emerald-500/20">
                    <span>👑 Lowest Price Recommendation</span>
                    {savings > 0 && <span>Save {savings}%</span>}
                </div>
            )}

            <div className="p-5 flex flex-col md:flex-row gap-6">
                {/* Image */}
                <div className="w-full md:w-48 h-48 flex-shrink-0 bg-slate-800 rounded-lg overflow-hidden flex items-center justify-center p-4">
                    {product.image_url ? (
                        <img src={product.image_url} alt="Product" className="max-h-full max-w-full object-contain mix-blend-screen" />
                    ) : (
                        <ShoppingCart className="w-12 h-12 text-slate-600" />
                    )}
                </div>

                {/* Content */}
                <div className="flex-1 space-y-4">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
                                {product.site}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full border font-medium ${decisionColor}`}>
                                {product.decision}
                            </span>
                        </div>

                        <h3 className="text-lg font-semibold leading-tight line-clamp-2" title={product.product_name}>
                            {product.product_name}
                        </h3>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm">
                        <div className="flex gap-1 items-center font-medium text-blue-400">
                            {product.currency} <span className="text-2xl font-bold text-white">{product.current_price.toLocaleString()}</span>
                        </div>
                        {product.rating && (
                            <div className="flex items-center gap-1 text-amber-400 bg-amber-400/10 px-2 py-1 rounded-md">
                                <Star className="w-4 h-4 fill-current" />
                                <span className="font-medium text-xs">{product.rating}</span>
                            </div>
                        )}
                        <div className={`px-2 py-1 rounded-md text-xs font-medium ${product.availability === 'In Stock' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {product.availability}
                        </div>
                    </div>

                    <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        Buy on {product.site}
                        <ExternalLink className="w-4 h-4" />
                    </a>
                </div>
            </div>
        </div>
    );
}
