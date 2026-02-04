import React, { useState, useEffect, useCallback } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
  Package, Users, FileText, CreditCard, MessageSquare, AlertTriangle,
  Bell, Settings, Home, Send, RefreshCw, CheckCircle, XCircle,
  IndianRupee, TrendingUp, Clock, Search, Plus, Menu, X
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// API Client
const api = axios.create({
  baseURL: API,
  timeout: 30000,
});

// Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={fetchStats}
          className="flex items-center gap-2 px-4 py-2 text-sm bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200 transition-colors"
          data-testid="refresh-btn"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Today's Sales"
          value={`₹${(stats?.today_sales || 0).toLocaleString('en-IN')}`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="emerald"
          subtitle={`${stats?.today_invoices || 0} invoices`}
        />
        <StatCard
          title="Pending Udhaar"
          value={`₹${(stats?.total_pending_udhaar || 0).toLocaleString('en-IN')}`}
          icon={<CreditCard className="w-6 h-6" />}
          color="amber"
          subtitle="Total credit outstanding"
        />
        <StatCard
          title="Total Customers"
          value={stats?.total_customers || 0}
          icon={<Users className="w-6 h-6" />}
          color="blue"
          subtitle="Active customers"
        />
        <StatCard
          title="Low Stock Items"
          value={stats?.low_stock_count || 0}
          icon={<AlertTriangle className="w-6 h-6" />}
          color={stats?.low_stock_count > 0 ? 'red' : 'gray'}
          subtitle="Below reorder level"
        />
        <StatCard
          title="Pending Approvals"
          value={stats?.pending_approvals || 0}
          icon={<Bell className="w-6 h-6" />}
          color={stats?.pending_approvals > 0 ? 'orange' : 'gray'}
          subtitle="HITL requests"
        />
        <StatCard
          title="Today's Invoices"
          value={stats?.today_invoices || 0}
          icon={<FileText className="w-6 h-6" />}
          color="purple"
          subtitle="Generated today"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickActionButton
            icon={<FileText />}
            label="New Invoice"
            href="/invoices"
          />
          <QuickActionButton
            icon={<Users />}
            label="Add Customer"
            href="/customers"
          />
          <QuickActionButton
            icon={<Package />}
            label="Check Stock"
            href="/inventory"
          />
          <QuickActionButton
            icon={<CreditCard />}
            label="View Udhaar"
            href="/udhaar"
          />
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, icon, color, subtitle }) => {
  const colorClasses = {
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    gray: 'bg-gray-50 text-gray-600 border-gray-200',
  };

  return (
    <div className={`rounded-xl border p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium opacity-80">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm opacity-70">{subtitle}</div>
    </div>
  );
};

// Quick Action Button
const QuickActionButton = ({ icon, label, href }) => (
  <Link
    to={href}
    className="flex flex-col items-center gap-2 p-4 rounded-lg bg-gray-50 hover:bg-amber-50 hover:text-amber-700 transition-colors text-gray-600"
  >
    {React.cloneElement(icon, { className: 'w-6 h-6' })}
    <span className="text-sm font-medium">{label}</span>
  </Link>
);

// Customers Page
const CustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data.customers || []);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(c =>
    c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.phone?.includes(searchTerm)
  );

  return (
    <div className="space-y-6" data-testid="customers-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
          data-testid="search-input"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Name</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Phone</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Credit Balance</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Credit Limit</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredCustomers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{customer.name}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-600">{customer.phone}</td>
                  <td className="px-6 py-4">
                    <span className={`font-medium ${customer.total_credit > 0 ? 'text-amber-600' : 'text-emerald-600'}`}>
                      ₹{(customer.total_credit || 0).toLocaleString('en-IN')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    ₹{(customer.credit_limit || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4">
                    {customer.is_bulk_buyer ? (
                      <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
                        Bulk Buyer
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                        Regular
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredCustomers.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No customers found
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Inventory Page
const InventoryPage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ fabric: '', color: '' });

  useEffect(() => {
    fetchInventory();
  }, [filter]);

  const fetchInventory = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.fabric) params.append('fabric_type', filter.fabric);
      if (filter.color) params.append('color', filter.color);
      
      const response = await api.get(`/inventory?${params}`);
      setItems(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStockStatus = (item) => {
    if (item.quantity <= item.reorder_level * 0.5) return { color: 'red', label: 'Critical' };
    if (item.quantity <= item.reorder_level) return { color: 'amber', label: 'Low' };
    return { color: 'emerald', label: 'Good' };
  };

  return (
    <div className="space-y-6" data-testid="inventory-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={filter.fabric}
          onChange={(e) => setFilter({ ...filter, fabric: e.target.value })}
          className="px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Fabrics</option>
          <option value="silk">Silk</option>
          <option value="cotton">Cotton</option>
          <option value="polyester">Polyester</option>
          <option value="linen">Linen</option>
        </select>
        <select
          value={filter.color}
          onChange={(e) => setFilter({ ...filter, color: e.target.value })}
          className="px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-amber-500"
        >
          <option value="">All Colors</option>
          <option value="red">Red</option>
          <option value="blue">Blue</option>
          <option value="green">Green</option>
          <option value="white">White</option>
          <option value="black">Black</option>
          <option value="yellow">Yellow</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => {
            const status = getStockStatus(item);
            return (
              <div
                key={item.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{item.name}</h3>
                    <p className="text-sm text-gray-500">
                      {item.color} {item.fabric_type} | {item.width}"
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full bg-${status.color}-100 text-${status.color}-700`}>
                    {status.label}
                  </span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Stock</span>
                    <span className="font-medium text-gray-900">{item.quantity} {item.unit}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Reorder Level</span>
                    <span className="text-gray-600">{item.reorder_level} {item.unit}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Rate</span>
                    <span className="font-medium text-gray-900">₹{item.rate_per_unit}/{item.unit}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">HSN Code</span>
                    <span className="text-gray-600">{item.hsn_code}</span>
                  </div>
                </div>

                {/* Stock Bar */}
                <div className="mt-4">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-${status.color}-500 rounded-full`}
                      style={{ width: `${Math.min(100, (item.quantity / (item.reorder_level * 2)) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-gray-200">
          No inventory items found
        </div>
      )}
    </div>
  );
};

// Invoices Page
const InvoicesPage = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await api.get('/invoices');
      setInvoices(response.data.invoices || []);
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'emerald';
      case 'partial': return 'amber';
      case 'pending': return 'orange';
      case 'overdue': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="space-y-6" data-testid="invoices-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Invoice #</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Customer</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Date</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Amount</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {invoices.map((invoice) => {
                const statusColor = getStatusColor(invoice.payment_status);
                return (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-amber-600">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{invoice.customer_name}</div>
                      <div className="text-sm text-gray-500">{invoice.customer_phone}</div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {new Date(invoice.created_at).toLocaleDateString('en-IN')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        ₹{(invoice.grand_total || 0).toLocaleString('en-IN')}
                      </div>
                      {invoice.balance_due > 0 && (
                        <div className="text-sm text-amber-600">
                          Due: ₹{invoice.balance_due.toLocaleString('en-IN')}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full bg-${statusColor}-100 text-${statusColor}-700`}>
                        {invoice.payment_status?.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${invoice.invoice_type === 'pucca' ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'}`}>
                        {invoice.invoice_type === 'pucca' ? 'GST Invoice' : 'Kacha Bill'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {invoices.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No invoices found
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Udhaar Page
const UdhaarPage = () => {
  const [summary, setSummary] = useState(null);
  const [overdue, setOverdue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUdhaarData();
  }, []);

  const fetchUdhaarData = async () => {
    try {
      const [summaryRes, overdueRes] = await Promise.all([
        api.get('/udhaar/summary'),
        api.get('/udhaar/overdue')
      ]);
      setSummary(summaryRes.data);
      setOverdue(overdueRes.data.overdue_customers || []);
    } catch (error) {
      console.error('Failed to fetch udhaar data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="udhaar-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Udhaar Management</h1>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-amber-50 rounded-xl border border-amber-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <IndianRupee className="w-8 h-8 text-amber-600" />
                <span className="text-sm font-medium text-amber-700">Total Pending</span>
              </div>
              <div className="text-3xl font-bold text-amber-800">
                ₹{(summary?.total_pending || 0).toLocaleString('en-IN')}
              </div>
              <div className="text-sm text-amber-600 mt-2">
                {summary?.customer_count || 0} customers with pending balance
              </div>
            </div>

            <div className="bg-red-50 rounded-xl border border-red-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
                <span className="text-sm font-medium text-red-700">Overdue (30+ days)</span>
              </div>
              <div className="text-3xl font-bold text-red-800">
                {overdue.length} customers
              </div>
              <div className="text-sm text-red-600 mt-2">
                Require follow-up
              </div>
            </div>
          </div>

          {/* Overdue List */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Overdue Customers</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {overdue.map((customer) => (
                <div key={customer._id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">{customer.customer_name}</div>
                    <div className="text-sm text-gray-500">{customer.customer_phone}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {customer.invoice_count} invoice(s) overdue
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-red-600">
                      ₹{(customer.total_overdue || 0).toLocaleString('en-IN')}
                    </div>
                    <button className="mt-2 px-3 py-1 text-xs font-medium bg-amber-100 text-amber-700 rounded-full hover:bg-amber-200">
                      Send Reminder
                    </button>
                  </div>
                </div>
              ))}
              {overdue.length === 0 && (
                <div className="px-6 py-12 text-center text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500" />
                  No overdue payments!
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// HITL Approvals Page
const ApprovalsPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await api.get('/hitl/pending');
      setRequests(response.data.requests || []);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      await api.post(`/hitl/${requestId}/approve`);
      fetchRequests();
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleReject = async (requestId) => {
    try {
      await api.post(`/hitl/${requestId}/reject`);
      fetchRequests();
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  return (
    <div className="space-y-6" data-testid="approvals-page">
      <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((request) => (
            <div
              key={request.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-700 rounded-full">
                    {request.request_type?.replace('_', ' ').toUpperCase()}
                  </span>
                  <h3 className="font-semibold text-gray-900 mt-2">
                    {request.customer_name}
                  </h3>
                  {request.amount && (
                    <p className="text-2xl font-bold text-amber-600 mt-1">
                      ₹{request.amount.toLocaleString('en-IN')}
                    </p>
                  )}
                  <p className="text-sm text-gray-500 mt-2">
                    Requested: {new Date(request.requested_at).toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(request.id)}
                    className="flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg hover:bg-emerald-200"
                    data-testid="approve-btn"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleReject(request.id)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                    data-testid="reject-btn"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
          {requests.length === 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-emerald-500" />
              <h3 className="text-lg font-medium text-gray-900">All caught up!</h3>
              <p className="text-gray-500 mt-1">No pending approvals</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Messages Page (Conversation Simulator)
const MessagesPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/test/process-text', {
        text: input,
        phone: 'web_dashboard_user'
      });

      const botMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Failed to process message:', error);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Error processing your message. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col" data-testid="messages-page">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Test Agent</h1>
      
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Test the Bharat Biz-Agent here!</p>
              <p className="text-sm mt-2">Try: "Ramesh ko 5000 ka bill bhejo"</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-amber-500 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-none">
                <RefreshCw className="w-5 h-5 animate-spin text-amber-600" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message in Hinglish..."
              className="flex-1 px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
              data-testid="message-input"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="send-btn"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sidebar Navigation
const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: <Home />, label: 'Dashboard' },
    { path: '/customers', icon: <Users />, label: 'Customers' },
    { path: '/inventory', icon: <Package />, label: 'Inventory' },
    { path: '/invoices', icon: <FileText />, label: 'Invoices' },
    { path: '/udhaar', icon: <CreditCard />, label: 'Udhaar' },
    { path: '/approvals', icon: <Bell />, label: 'Approvals' },
    { path: '/messages', icon: <MessageSquare />, label: 'Test Agent' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-gradient-to-b from-amber-900 to-amber-950 transform transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-white">Bharat Biz-Agent</h1>
              <p className="text-amber-300 text-sm">Kapoor Textiles</p>
            </div>
            <button onClick={onClose} className="lg:hidden text-white">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <nav className="px-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-amber-600 text-white'
                    : 'text-amber-200 hover:bg-amber-800 hover:text-white'
                }`}
              >
                {React.cloneElement(item.icon, { className: 'w-5 h-5' })}
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-6">
          <div className="bg-amber-800/50 rounded-lg p-4">
            <p className="text-amber-200 text-sm">WhatsApp Webhook:</p>
            <p className="text-white text-xs font-mono mt-1 break-all">
              /api/webhook
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

// Main App Layout
const AppLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Mobile Header */}
      <header className="lg:hidden bg-white shadow-sm border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-600 hover:text-gray-900"
          >
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-bold text-amber-900">Bharat Biz-Agent</h1>
          <div className="w-6" />
        </div>
      </header>

      {/* Main Content */}
      <main className="lg:ml-64 p-6">
        {children}
      </main>
    </div>
  );
};

// Main App
function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/invoices" element={<InvoicesPage />} />
          <Route path="/udhaar" element={<UdhaarPage />} />
          <Route path="/approvals" element={<ApprovalsPage />} />
          <Route path="/messages" element={<MessagesPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
