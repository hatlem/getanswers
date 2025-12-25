import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ArrowLeft,
  Shield,
  CreditCard,
  Users,
  Building2,
  BarChart3,
  Plus,
  Edit2,
  Archive,
  Loader2,
  AlertCircle,
  CheckCircle2,
  DollarSign,
  Package,
  Tag,
} from 'lucide-react';
import { adminApi, type StripeProduct, type StripePrice, type PlatformStats, type StripeConfig } from '../../lib/api';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

type TabId = 'overview' | 'products' | 'users';

const planTierColors: Record<string, string> = {
  free: 'text-text-secondary bg-surface-border',
  starter: 'text-warning bg-warning/20',
  pro: 'text-accent-cyan bg-accent-cyan/20',
  enterprise: 'text-accent-purple bg-accent-purple/20',
};

export function AdminPage() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [showCreateProduct, setShowCreateProduct] = useState(false);
  const [showCreatePrice, setShowCreatePrice] = useState<string | null>(null);
  const [editingProduct, setEditingProduct] = useState<StripeProduct | null>(null);
  const queryClient = useQueryClient();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminApi.getStats,
  });

  const { data: stripeConfig } = useQuery({
    queryKey: ['admin-stripe-config'],
    queryFn: adminApi.getStripeConfig,
  });

  const { data: products, isLoading: productsLoading, refetch: refetchProducts } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => adminApi.listProducts(true),
  });

  const tabs = [
    { id: 'overview' as TabId, label: 'Overview', icon: BarChart3 },
    { id: 'products' as TabId, label: 'Stripe Products', icon: Package },
    { id: 'users' as TabId, label: 'Users', icon: Users },
  ];

  return (
    <div className="min-h-screen bg-surface-base">
      <div className="max-w-6xl mx-auto px-4 py-6 md:p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-accent-purple" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-text-primary">Super Admin</h1>
              <p className="text-sm text-text-secondary">Platform management & Stripe products</p>
            </div>
          </div>
        </motion.div>

        {/* Stripe Mode Badge */}
        {stripeConfig && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={cn(
              'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium mb-6',
              stripeConfig.mode === 'live'
                ? 'bg-success/20 text-success'
                : 'bg-warning/20 text-warning'
            )}
          >
            <CreditCard className="w-3.5 h-3.5" />
            Stripe {stripeConfig.mode.toUpperCase()} Mode
          </motion.div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px',
                activeTab === tab.id
                  ? 'border-accent-cyan text-accent-cyan'
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              )}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <OverviewTab stats={stats} loading={statsLoading} />
        )}

        {activeTab === 'products' && (
          <ProductsTab
            products={products}
            loading={productsLoading}
            stripeConfig={stripeConfig}
            onRefetch={refetchProducts}
            showCreateProduct={showCreateProduct}
            setShowCreateProduct={setShowCreateProduct}
            showCreatePrice={showCreatePrice}
            setShowCreatePrice={setShowCreatePrice}
            editingProduct={editingProduct}
            setEditingProduct={setEditingProduct}
          />
        )}

        {activeTab === 'users' && (
          <UsersTab />
        )}
      </div>
    </div>
  );
}

// Overview Tab
function OverviewTab({ stats, loading }: { stats?: PlatformStats; loading: boolean }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-accent-cyan" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-2 md:grid-cols-4 gap-4"
    >
      <StatCard
        label="Total Users"
        value={stats?.total_users || 0}
        icon={Users}
        color="text-accent-cyan"
      />
      <StatCard
        label="Organizations"
        value={stats?.total_organizations || 0}
        icon={Building2}
        color="text-accent-purple"
      />
      <StatCard
        label="Subscriptions"
        value={stats?.total_subscriptions || 0}
        icon={CreditCard}
        color="text-success"
      />
      <StatCard
        label="New This Week"
        value={stats?.recent_signups || 0}
        icon={BarChart3}
        color="text-warning"
      />

      {/* Plan Breakdown */}
      <div className="col-span-2 md:col-span-4 bg-surface-card border border-surface-border rounded-xl p-4">
        <h3 className="text-sm font-medium text-text-secondary mb-3">Users by Plan</h3>
        <div className="flex flex-wrap gap-3">
          {stats?.users_by_plan && Object.entries(stats.users_by_plan).map(([plan, count]) => (
            <div
              key={plan}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium',
                planTierColors[plan] || 'text-text-secondary bg-surface-border'
              )}
            >
              {plan}: {count}
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ElementType; color: string }) {
  return (
    <div className="bg-surface-card border border-surface-border rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center bg-surface-border', color)}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-text-primary">{value}</p>
          <p className="text-xs text-text-muted">{label}</p>
        </div>
      </div>
    </div>
  );
}

// Products Tab
function ProductsTab({
  products,
  loading,
  stripeConfig,
  onRefetch,
  showCreateProduct,
  setShowCreateProduct,
  showCreatePrice,
  setShowCreatePrice,
  editingProduct,
  setEditingProduct,
}: {
  products?: StripeProduct[];
  loading: boolean;
  stripeConfig?: StripeConfig;
  onRefetch: () => void;
  showCreateProduct: boolean;
  setShowCreateProduct: (show: boolean) => void;
  showCreatePrice: string | null;
  setShowCreatePrice: (productId: string | null) => void;
  editingProduct: StripeProduct | null;
  setEditingProduct: (product: StripeProduct | null) => void;
}) {
  const queryClient = useQueryClient();

  const archiveProductMutation = useMutation({
    mutationFn: adminApi.archiveProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-products'] });
    },
  });

  const archivePriceMutation = useMutation({
    mutationFn: adminApi.archivePrice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-products'] });
    },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-accent-cyan" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-secondary">
          Manage Stripe products and prices for GetAnswers
        </p>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setShowCreateProduct(true)}
        >
          <Plus className="w-4 h-4 mr-2" />
          New Product
        </Button>
      </div>

      {/* Create Product Form */}
      {showCreateProduct && (
        <CreateProductForm
          onClose={() => setShowCreateProduct(false)}
          onSuccess={() => {
            setShowCreateProduct(false);
            onRefetch();
          }}
        />
      )}

      {/* Products List */}
      {products && products.length > 0 ? (
        <div className="space-y-4">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onArchive={() => archiveProductMutation.mutate(product.id)}
              onEdit={() => setEditingProduct(product)}
              onAddPrice={() => setShowCreatePrice(product.id)}
              onArchivePrice={(priceId) => archivePriceMutation.mutate(priceId)}
              showCreatePrice={showCreatePrice === product.id}
              onCloseCreatePrice={() => setShowCreatePrice(null)}
              onPriceCreated={onRefetch}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-surface-card border border-surface-border rounded-xl">
          <Package className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No products found</p>
          <p className="text-sm text-text-muted mt-1">Create your first product to get started</p>
        </div>
      )}
    </motion.div>
  );
}

function ProductCard({
  product,
  onArchive,
  onEdit,
  onAddPrice,
  onArchivePrice,
  showCreatePrice,
  onCloseCreatePrice,
  onPriceCreated,
}: {
  product: StripeProduct;
  onArchive: () => void;
  onEdit: () => void;
  onAddPrice: () => void;
  onArchivePrice: (priceId: string) => void;
  showCreatePrice: boolean;
  onCloseCreatePrice: () => void;
  onPriceCreated: () => void;
}) {
  const planTier = product.metadata?.plan_tier;

  return (
    <div className={cn(
      'bg-surface-card border rounded-xl p-4',
      product.active ? 'border-surface-border' : 'border-error/30 opacity-60'
    )}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
            <Package className="w-5 h-5 text-accent-cyan" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-text-primary">{product.name}</h3>
              {!product.active && (
                <span className="text-xs px-2 py-0.5 rounded bg-error/20 text-error">Archived</span>
              )}
            </div>
            <p className="text-xs text-text-muted">{product.id}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {planTier && (
            <span className={cn(
              'px-2 py-0.5 rounded text-xs font-medium',
              planTierColors[planTier] || 'text-text-secondary bg-surface-border'
            )}>
              {planTier}
            </span>
          )}
          <button
            onClick={onAddPrice}
            className="p-1.5 text-text-secondary hover:text-accent-cyan transition-colors"
            title="Add Price"
          >
            <Plus className="w-4 h-4" />
          </button>
          {product.active && (
            <button
              onClick={onArchive}
              className="p-1.5 text-text-secondary hover:text-error transition-colors"
              title="Archive Product"
            >
              <Archive className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {product.description && (
        <p className="text-sm text-text-secondary mb-3">{product.description}</p>
      )}

      {/* Create Price Form */}
      {showCreatePrice && (
        <CreatePriceForm
          productId={product.id}
          onClose={onCloseCreatePrice}
          onSuccess={() => {
            onCloseCreatePrice();
            onPriceCreated();
          }}
        />
      )}

      {/* Prices */}
      {product.prices.length > 0 && (
        <div className="mt-3 border-t border-surface-border pt-3">
          <p className="text-xs text-text-muted mb-2">Prices</p>
          <div className="space-y-2">
            {product.prices.map((price) => (
              <PriceRow
                key={price.id}
                price={price}
                onArchive={() => onArchivePrice(price.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PriceRow({ price, onArchive }: { price: StripePrice; onArchive: () => void }) {
  const formatPrice = (amount: number | null, currency: string) => {
    if (amount === null) return 'Custom';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount / 100);
  };

  return (
    <div className={cn(
      'flex items-center justify-between p-2 rounded-lg',
      price.active ? 'bg-surface-border/50' : 'bg-error/10 opacity-60'
    )}>
      <div className="flex items-center gap-3">
        <Tag className="w-4 h-4 text-text-muted" />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-text-primary">
              {formatPrice(price.unit_amount, price.currency)}
            </span>
            {price.recurring_interval && (
              <span className="text-xs text-text-muted">
                /{price.recurring_interval}
              </span>
            )}
            {price.nickname && (
              <span className="text-xs text-text-secondary">({price.nickname})</span>
            )}
            {!price.active && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-error/20 text-error">Archived</span>
            )}
          </div>
          <p className="text-xs text-text-muted">{price.id}</p>
        </div>
      </div>
      {price.active && (
        <button
          onClick={onArchive}
          className="p-1 text-text-secondary hover:text-error transition-colors"
          title="Archive Price"
        >
          <Archive className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}

function CreateProductForm({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [planTier, setPlanTier] = useState<'starter' | 'pro' | 'enterprise'>('starter');

  const mutation = useMutation({
    mutationFn: adminApi.createProduct,
    onSuccess: () => {
      onSuccess();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ name, description: description || undefined, plan_tier: planTier });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-surface-card border border-accent-cyan/30 rounded-xl p-4 space-y-3">
      <h4 className="font-medium text-text-primary">Create New Product</h4>

      <div>
        <label className="block text-xs text-text-secondary mb-1">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 bg-surface-base border border-surface-border rounded-lg text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
          placeholder="e.g., Pro Plan"
          required
        />
      </div>

      <div>
        <label className="block text-xs text-text-secondary mb-1">Description</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 bg-surface-base border border-surface-border rounded-lg text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
          placeholder="Optional description"
        />
      </div>

      <div>
        <label className="block text-xs text-text-secondary mb-1">Plan Tier</label>
        <select
          value={planTier}
          onChange={(e) => setPlanTier(e.target.value as 'starter' | 'pro' | 'enterprise')}
          className="w-full px-3 py-2 bg-surface-base border border-surface-border rounded-lg text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
        >
          <option value="starter">Starter</option>
          <option value="pro">Pro</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      <div className="flex gap-2 pt-2">
        <Button type="button" variant="outline" size="sm" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending || !name}>
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Product'}
        </Button>
      </div>

      {mutation.isError && (
        <p className="text-xs text-error">Failed to create product</p>
      )}
    </form>
  );
}

function CreatePriceForm({ productId, onClose, onSuccess }: { productId: string; onClose: () => void; onSuccess: () => void }) {
  const [amount, setAmount] = useState('');
  const [interval, setInterval] = useState<'month' | 'year'>('month');
  const [nickname, setNickname] = useState('');
  const [planTier, setPlanTier] = useState<'starter' | 'pro' | 'enterprise'>('starter');

  const mutation = useMutation({
    mutationFn: adminApi.createPrice,
    onSuccess: () => {
      onSuccess();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      product_id: productId,
      unit_amount: Math.round(parseFloat(amount) * 100),
      interval,
      nickname: nickname || undefined,
      plan_tier: planTier,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-surface-base border border-accent-cyan/30 rounded-lg p-3 mb-3 space-y-2">
      <h4 className="text-sm font-medium text-text-primary">Add Price</h4>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-text-secondary mb-1">Amount (USD)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full px-2 py-1.5 bg-surface-card border border-surface-border rounded text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
            placeholder="29.00"
            required
          />
        </div>
        <div>
          <label className="block text-xs text-text-secondary mb-1">Interval</label>
          <select
            value={interval}
            onChange={(e) => setInterval(e.target.value as 'month' | 'year')}
            className="w-full px-2 py-1.5 bg-surface-card border border-surface-border rounded text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
          >
            <option value="month">Monthly</option>
            <option value="year">Yearly</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-text-secondary mb-1">Nickname</label>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            className="w-full px-2 py-1.5 bg-surface-card border border-surface-border rounded text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
            placeholder="Optional"
          />
        </div>
        <div>
          <label className="block text-xs text-text-secondary mb-1">Plan Tier</label>
          <select
            value={planTier}
            onChange={(e) => setPlanTier(e.target.value as 'starter' | 'pro' | 'enterprise')}
            className="w-full px-2 py-1.5 bg-surface-card border border-surface-border rounded text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
          >
            <option value="starter">Starter</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>
      </div>

      <div className="flex gap-2 pt-1">
        <Button type="button" variant="outline" size="sm" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending || !amount}>
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Add Price'}
        </Button>
      </div>
    </form>
  );
}

// Users Tab (placeholder)
function UsersTab() {
  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.listUsers({ limit: 50 }),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-accent-cyan" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <p className="text-sm text-text-secondary">
        Showing {users?.length || 0} users
      </p>

      <div className="bg-surface-card border border-surface-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-surface-border/50">
            <tr>
              <th className="text-left text-xs font-medium text-text-secondary px-4 py-3">User</th>
              <th className="text-left text-xs font-medium text-text-secondary px-4 py-3">Admin</th>
              <th className="text-left text-xs font-medium text-text-secondary px-4 py-3">Joined</th>
            </tr>
          </thead>
          <tbody>
            {users?.map((user) => (
              <tr key={user.id} className="border-t border-surface-border">
                <td className="px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{user.name}</p>
                    <p className="text-xs text-text-muted">{user.email}</p>
                  </div>
                </td>
                <td className="px-4 py-3">
                  {user.is_super_admin && (
                    <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-accent-purple/20 text-accent-purple">
                      <Shield className="w-3 h-3" />
                      Super Admin
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-xs text-text-muted">
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
