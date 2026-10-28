"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Building2,
  Receipt,
  Layers,
  ArrowRight,
  RefreshCw,
  Search,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  Hash,
  Calendar,
  DollarSign,
  ChevronRight,
  Database,
  History,
  Sparkles,
  Eye,
  Download
} from "lucide-react";

interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

interface VendorInfo {
  name: string;
  tax_id: string;
  address?: string;
}

interface InvoiceDocument {
  invoice_number: string;
  issue_date: string;
  due_date?: string;
  vendor: VendorInfo;
  po_number?: string;
  currency: string;
  line_items: LineItem[];
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  _confidence?: Record<string, number>;
  confidence?: Record<string, number>;
}

interface Violation {
  code: string;
  severity: "blocker" | "warning";
  field?: string;
  message: string;
  expected?: any;
  actual?: any;
}

interface Decision {
  outcome: "APPROVE" | "REVIEW" | "REJECT";
  violations: Violation[];
  processed_at: string;
  invoice_summary?: any;
  file_name?: string;
}

interface SampleInvoice {
  filename: string;
  invoice_number: string;
  vendor_name: string;
  tax_id: string;
  po_number: string;
  total: number;
  currency: string;
  notes: string;
  expected_outcome: "APPROVE" | "REVIEW" | "REJECT";
  tag_color: string;
}

interface VendorMaster {
  id: string;
  name: string;
  tax_id: string;
  status: string;
  payment_terms_days: number;
  credit_limit: number;
}

interface POMaster {
  po_number: string;
  vendor_id: string;
  total_amount: number;
  status: string;
  lines: any[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function InvoiceAgentDashboard() {
  const [activeTab, setActiveTab] = useState<"extract" | "samples" | "master-data" | "history">("extract");
  const [samples, setSamples] = useState<SampleInvoice[]>([]);
  const [vendors, setVendors] = useState<VendorMaster[]>([]);
  const [pos, setPos] = useState<POMaster[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeSampleName, setActiveSampleName] = useState<string | null>(null);
  const [currentInvoice, setCurrentInvoice] = useState<InvoiceDocument | null>(null);
  const [currentDecision, setCurrentDecision] = useState<Decision | null>(null);
  const [activeViewMode, setActiveViewMode] = useState<"data" | "json">("data");
  const [searchFilter, setSearchFilter] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load sample data & master data
  useEffect(() => {
    fetchSamples();
    fetchVendors();
    fetchPOs();
    fetchHistory();
  }, []);

  const fetchSamples = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/samples`);
      if (res.ok) {
        const data = await res.json();
        setSamples(data);
      }
    } catch (e) {
      console.warn("Could not load samples:", e);
    }
  };

  const fetchVendors = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/vendors`);
      if (res.ok) setVendors(await res.json());
    } catch (e) {
      console.warn("Could not load vendors:", e);
    }
  };

  const fetchPOs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/pos`);
      if (res.ok) setPos(await res.json());
    } catch (e) {
      console.warn("Could not load POs:", e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      if (res.ok) setHistory(await res.json());
    } catch (e) {
      console.warn("Could not load history:", e);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setSelectedFile(file);
    setActiveSampleName(null);
    await processUploadedFile(file);
  };

  const processUploadedFile = async (file: File) => {
    setIsProcessing(true);
    setCurrentDecision(null);
    setCurrentInvoice(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/api/review`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setCurrentInvoice(data.invoice);
        setCurrentDecision(data.decision);
        setActiveTab("extract");
        fetchHistory();
      } else {
        alert(`Lỗi xử lý hóa đơn: ${data.detail || "Không rõ nguyên nhân"}`);
      }
    } catch (err: any) {
      alert(`Không thể kết nối đến Backend: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const runSample = async (sample: SampleInvoice) => {
    setIsProcessing(true);
    setActiveSampleName(sample.filename);
    setSelectedFile(null);
    setCurrentDecision(null);
    setCurrentInvoice(null);
    setActiveTab("extract");

    try {
      const res = await fetch(`${API_BASE}/api/samples/${sample.filename}/run`, {
        method: "POST",
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setCurrentInvoice(data.invoice);
        setCurrentDecision(data.decision);
        fetchHistory();
      } else {
        alert(`Lỗi xử lý mẫu: ${data.detail || "Không rõ nguyên nhân"}`);
      }
    } catch (err: any) {
      alert(`Lỗi thẩm định hóa đơn mẫu: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const getConfidenceBadge = (field: string) => {
    if (!currentInvoice) return null;
    const confObj = currentInvoice.confidence || currentInvoice._confidence || {};
    const val = confObj[field] ?? 0.95;
    const pct = Math.round(val * 100);

    if (val >= 0.90) {
      return (
        <span className="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
          {pct}% tin cậy
        </span>
      );
    } else if (val >= 0.70) {
      return (
        <span className="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-950 text-amber-400 border border-amber-800">
          {pct}% trung bình
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-rose-950 text-rose-400 border border-rose-800 animate-pulse">
          {pct}% thấp (Cảnh báo)
        </span>
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-30 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-sky-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Receipt className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold tracking-tight text-white">Invoice Extraction & Approval Agent</h1>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  Enterprise v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Trích xuất dữ liệu có cấu trúc & Ra quyết định phê duyệt kế toán tự động (10 Rules)
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 bg-slate-800/50 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("extract")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                activeTab === "extract"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>Thẩm định hóa đơn</span>
            </button>
            <button
              onClick={() => setActiveTab("samples")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                activeTab === "samples"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>20 Hóa đơn mẫu</span>
              <span className="ml-1 px-1.5 py-0.2 rounded-full bg-indigo-900/60 text-[10px] text-indigo-200 border border-indigo-700">
                {samples.length || 20}
              </span>
            </button>
            <button
              onClick={() => setActiveTab("master-data")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                activeTab === "master-data"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Database className="w-4 h-4" />
              <span>Master Data ({vendors.length} Vendors)</span>
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                activeTab === "history"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <History className="w-4 h-4" />
              <span>Audit Log ({history.length})</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto w-full p-6 flex-1">
        {/* TAB 1: THẨM ĐỊNH HÓA ĐƠN */}
        {activeTab === "extract" && (
          <div className="space-y-6">
            {/* Top Bar with Quick Upload & Sample Quick Selector */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Upload Card */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                      <FileText className="w-4 h-4 text-indigo-400" />
                      <span>Tải lên hóa đơn mới</span>
                    </span>
                    {activeSampleName && (
                      <span className="text-[11px] text-indigo-400 bg-indigo-950/80 border border-indigo-800 px-2 py-0.5 rounded-full">
                        Đang chọn mẫu: {activeSampleName}
                      </span>
                    )}
                  </div>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    accept=".pdf,.png,.jpg,.jpeg"
                    className="hidden"
                  />
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-indigo-500/80 bg-slate-950/40 hover:bg-indigo-950/20 rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center space-y-2 group"
                  >
                    <div className="w-12 h-12 rounded-full bg-slate-800 group-hover:bg-indigo-600/20 group-hover:text-indigo-400 flex items-center justify-center text-slate-400 transition">
                      <UploadCloud className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-200">Kéo thả file PDF / Ảnh hóa đơn vào đây</p>
                      <p className="text-xs text-slate-500 mt-0.5">hoặc bấm để chọn file từ máy tính (Hỗ trợ PDF 1-3 trang, JPG, PNG)</p>
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                  <span>Trích xuất độc lập & Khớp Rule Engine</span>
                  <button
                    onClick={() => setActiveTab("samples")}
                    className="text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
                  >
                    <span>Chọn từ 20 mẫu có sẵn</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Sample Quick Selector */}
              <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                      <Sparkles className="w-4 h-4 text-emerald-400" />
                      <span>Thử nhanh các tình huống thẩm định (1-Click Run)</span>
                    </span>
                    <span className="text-xs text-slate-500">10 Hợp lệ · 10 Cố ý vi phạm</span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {/* 4 Representative Quick Buttons */}
                    <button
                      onClick={() => samples.length > 0 && runSample(samples[0])}
                      className="p-2.5 rounded-xl border border-emerald-900/50 bg-emerald-950/20 hover:bg-emerald-950/40 text-left transition group"
                    >
                      <div className="flex items-center justify-between text-[11px] font-semibold text-emerald-400 mb-1">
                        <span>INV-2026-001</span>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-medium text-slate-200 truncate">TechCore Solutions</p>
                      <p className="text-[10px] text-emerald-500/80 mt-1">Kỳ vọng: APPROVE</p>
                    </button>

                    <button
                      onClick={() => samples.find(s => s.filename.includes("UNKNOWN")) && runSample(samples.find(s => s.filename.includes("UNKNOWN"))!)}
                      className="p-2.5 rounded-xl border border-rose-900/50 bg-rose-950/20 hover:bg-rose-950/40 text-left transition group"
                    >
                      <div className="flex items-center justify-between text-[11px] font-semibold text-rose-400 mb-1">
                        <span>VENDOR_UNKNOWN</span>
                        <XCircle className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-medium text-slate-200 truncate">Ghost Technologies</p>
                      <p className="text-[10px] text-rose-500/80 mt-1">Kỳ vọng: REJECT</p>
                    </button>

                    <button
                      onClick={() => samples.find(s => s.filename.includes("BLOCKED")) && runSample(samples.find(s => s.filename.includes("BLOCKED"))!)}
                      className="p-2.5 rounded-xl border border-rose-900/50 bg-rose-950/20 hover:bg-rose-950/40 text-left transition group"
                    >
                      <div className="flex items-center justify-between text-[11px] font-semibold text-rose-400 mb-1">
                        <span>VENDOR_BLOCKED</span>
                        <XCircle className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-medium text-slate-200 truncate">Nexus Furniture</p>
                      <p className="text-[10px] text-rose-500/80 mt-1">Kỳ vọng: REJECT</p>
                    </button>

                    <button
                      onClick={() => samples.find(s => s.filename.includes("PAYMENT_TERMS")) && runSample(samples.find(s => s.filename.includes("PAYMENT_TERMS"))!)}
                      className="p-2.5 rounded-xl border border-amber-900/50 bg-amber-950/20 hover:bg-amber-950/40 text-left transition group"
                    >
                      <div className="flex items-center justify-between text-[11px] font-semibold text-amber-400 mb-1">
                        <span>TERMS_ODD</span>
                        <AlertTriangle className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-medium text-slate-200 truncate">Apex Logistics</p>
                      <p className="text-[10px] text-amber-500/80 mt-1">Kỳ vọng: REVIEW</p>
                    </button>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60">
                  <span className="text-xs text-slate-400">
                    Bấm bất kỳ mẫu nào để kích hoạt toàn bộ quy trình: Trích xuất → Validate → Rule Engine → Decision
                  </span>
                  <button
                    onClick={() => setActiveTab("samples")}
                    className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center space-x-1"
                  >
                    <span>Xem toàn bộ 20 kịch bản</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Loading Indicator */}
            {isProcessing && (
              <div className="bg-slate-900/90 border border-indigo-500/50 rounded-2xl p-8 text-center flex flex-col items-center justify-center space-y-3 animate-pulse">
                <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
                <div>
                  <h3 className="text-base font-bold text-white">Đang thực thi quy trình thẩm định hóa đơn...</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Chuẩn hóa tài liệu → Trích xuất cấu trúc JSON → Kiểm tra số học → Đối chiếu 10 business rules Master Data
                  </p>
                </div>
              </div>
            )}

            {/* RESULTS VIEW */}
            {currentDecision && currentInvoice && !isProcessing && (
              <div className="space-y-6">
                {/* 1. Large Decision Banner */}
                <div
                  className={`rounded-2xl p-6 border transition shadow-xl ${
                    currentDecision.outcome === "APPROVE"
                      ? "bg-gradient-to-r from-emerald-950/60 via-slate-900 to-slate-900 border-emerald-500/40 shadow-emerald-950/40"
                      : currentDecision.outcome === "REVIEW"
                      ? "bg-gradient-to-r from-amber-950/60 via-slate-900 to-slate-900 border-amber-500/40 shadow-amber-950/40"
                      : "bg-gradient-to-r from-rose-950/60 via-slate-900 to-slate-900 border-rose-500/40 shadow-rose-950/40"
                  }`}
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="flex items-center space-x-4">
                      <div
                        className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg ${
                          currentDecision.outcome === "APPROVE"
                            ? "bg-emerald-500 text-slate-950"
                            : currentDecision.outcome === "REVIEW"
                            ? "bg-amber-500 text-slate-950"
                            : "bg-rose-500 text-slate-950"
                        }`}
                      >
                        {currentDecision.outcome === "APPROVE" && <CheckCircle2 className="w-8 h-8 stroke-[2.5]" />}
                        {currentDecision.outcome === "REVIEW" && <AlertTriangle className="w-8 h-8 stroke-[2.5]" />}
                        {currentDecision.outcome === "REJECT" && <XCircle className="w-8 h-8 stroke-[2.5]" />}
                      </div>

                      <div>
                        <div className="flex items-center space-x-3">
                          <span className="text-xs font-semibold text-slate-400">QUYẾT ĐỊNH PHÊ DUYỆT:</span>
                          <span
                            className={`text-2xl font-black tracking-wider px-3 py-0.5 rounded-lg border ${
                              currentDecision.outcome === "APPROVE"
                                ? "bg-emerald-950 text-emerald-400 border-emerald-700"
                                : currentDecision.outcome === "REVIEW"
                                ? "bg-amber-950 text-amber-400 border-amber-700"
                                : "bg-rose-950 text-rose-400 border-rose-700"
                            }`}
                          >
                            {currentDecision.outcome}
                          </span>
                        </div>
                        <p className="text-sm text-slate-300 mt-1">
                          {currentDecision.outcome === "APPROVE" &&
                            "Hóa đơn hoàn toàn hợp lệ. Khớp Master Data nhà cung cấp, mã PO, thỏa mãn hạn mức và đúng tuyệt đối về số học."}
                          {currentDecision.outcome === "REVIEW" &&
                            "Phát hiện cảnh báo hoặc độ tin cậy thấp. Cần kế toán viên kiểm tra lại mắt thường trước khi giải ngân."}
                          {currentDecision.outcome === "REJECT" &&
                            "Từ chối thanh toán do vi phạm các quy tắc kiểm soát rủi ro nghiêm ngặt (Blocker violations)."}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-right">
                      <div>
                        <span className="text-xs text-slate-500 block">Số sai lệch phát hiện</span>
                        <span
                          className={`text-xl font-bold ${
                            currentDecision.violations.length === 0 ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {currentDecision.violations.length} lỗi
                        </span>
                      </div>
                      <div className="border-l border-slate-800 pl-4">
                        <span className="text-xs text-slate-500 block">Tổng tiền hóa đơn</span>
                        <span className="text-xl font-bold text-white">
                          ${currentInvoice.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {currentInvoice.currency}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 2. Violations List if any */}
                {currentDecision.violations.length > 0 && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-rose-400" />
                        <span>Danh sách sai lệch & Lý do từ chối (Violations List)</span>
                      </h3>
                      <span className="text-xs text-slate-500">Mỗi rule trích dẫn cụ thể trường dữ liệu gây lỗi</span>
                    </div>

                    <div className="space-y-2.5">
                      {currentDecision.violations.map((violation, idx) => (
                        <div
                          key={idx}
                          className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                            violation.severity === "blocker"
                              ? "bg-rose-950/20 border-rose-900/60"
                              : "bg-amber-950/20 border-amber-900/60"
                          }`}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <span
                                className={`text-[11px] font-black uppercase px-2 py-0.5 rounded ${
                                  violation.severity === "blocker"
                                    ? "bg-rose-900 text-rose-200"
                                    : "bg-amber-900 text-amber-200"
                                }`}
                              >
                                {violation.severity}
                              </span>
                              <span className="font-mono text-xs font-bold text-slate-200">{violation.code}</span>
                              {violation.field && (
                                <span className="text-xs text-slate-400">
                                  (Trường: <span className="font-mono text-indigo-400">{violation.field}</span>)
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-slate-300 font-medium">{violation.message}</p>
                          </div>

                          {(violation.expected || violation.actual) && (
                            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-xs font-mono min-w-[240px]">
                              {violation.expected && (
                                <div className="text-emerald-400 truncate">
                                  <span className="text-slate-500">Kỳ vọng: </span>
                                  {String(violation.expected)}
                                </div>
                              )}
                              {violation.actual && (
                                <div className="text-rose-400 truncate">
                                  <span className="text-slate-500">Thực tế: </span>
                                  {String(violation.actual)}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 3. Side-by-side Extracted Invoice Data & JSON */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-bold text-slate-200 flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-indigo-400" />
                        <span>Dữ liệu hóa đơn trích xuất (InvoiceDocument)</span>
                      </span>
                      <span className="text-xs text-slate-500">#{currentInvoice.invoice_number}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
                        <button
                          onClick={() => setActiveViewMode("data")}
                          className={`px-3 py-1 text-xs font-semibold rounded ${
                            activeViewMode === "data" ? "bg-indigo-600 text-white" : "text-slate-400"
                          }`}
                        >
                          Trực quan
                        </button>
                        <button
                          onClick={() => setActiveViewMode("json")}
                          className={`px-3 py-1 text-xs font-semibold rounded ${
                            activeViewMode === "json" ? "bg-indigo-600 text-white" : "text-slate-400"
                          }`}
                        >
                          Raw JSON
                        </button>
                      </div>

                      {activeSampleName && (
                        <a
                          href={`${API_BASE}/api/samples/${activeSampleName}/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center space-x-1 border border-slate-700"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Xem PDF gốc</span>
                        </a>
                      )}
                    </div>
                  </div>

                  {activeViewMode === "data" ? (
                    <div className="p-6 space-y-6">
                      {/* Key Metadata Cards */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <Building2 className="w-3.5 h-3.5" />
                              <span>Nhà cung cấp</span>
                            </span>
                            {getConfidenceBadge("vendor_name")}
                          </div>
                          <p className="font-semibold text-sm text-slate-100">{currentInvoice.vendor.name}</p>
                          <p className="text-xs text-slate-500 font-mono mt-0.5">MST: {currentInvoice.vendor.tax_id}</p>
                        </div>

                        <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <Hash className="w-3.5 h-3.5" />
                              <span>Số hóa đơn</span>
                            </span>
                            {getConfidenceBadge("invoice_number")}
                          </div>
                          <p className="font-semibold text-sm text-slate-100 font-mono">#{currentInvoice.invoice_number}</p>
                          <p className="text-xs text-indigo-400 font-mono mt-0.5">
                            PO: {currentInvoice.po_number || "Không đính kèm"}
                          </p>
                        </div>

                        <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <Calendar className="w-3.5 h-3.5" />
                              <span>Ngày lập / Hạn TT</span>
                            </span>
                            {getConfidenceBadge("issue_date")}
                          </div>
                          <p className="font-semibold text-sm text-slate-100">{currentInvoice.issue_date}</p>
                          <p className="text-xs text-slate-500 mt-0.5">Hạn: {currentInvoice.due_date || "N/A"}</p>
                        </div>

                        <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-slate-400 flex items-center space-x-1">
                              <DollarSign className="w-3.5 h-3.5" />
                              <span>Tổng thanh toán</span>
                            </span>
                            {getConfidenceBadge("total_amount")}
                          </div>
                          <p className="font-bold text-base text-emerald-400">
                            ${currentInvoice.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}{" "}
                            {currentInvoice.currency}
                          </p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            Tiền hàng: ${currentInvoice.subtotal.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                          </p>
                        </div>
                      </div>

                      {/* Line Items Table */}
                      <div className="border border-slate-800 rounded-xl overflow-hidden">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                            <tr>
                              <th className="px-4 py-3">#</th>
                              <th className="px-4 py-3">Mô tả sản phẩm / Dịch vụ</th>
                              <th className="px-4 py-3 text-right">Số lượng</th>
                              <th className="px-4 py-3 text-right">Đơn giá</th>
                              <th className="px-4 py-3 text-right">Thành tiền</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60">
                            {currentInvoice.line_items.map((item, idx) => (
                              <tr key={idx} className="hover:bg-slate-800/30">
                                <td className="px-4 py-3 text-slate-500">{idx + 1}</td>
                                <td className="px-4 py-3 font-medium text-slate-200">{item.description}</td>
                                <td className="px-4 py-3 text-right font-mono text-slate-300">{item.quantity}</td>
                                <td className="px-4 py-3 text-right font-mono text-slate-300">
                                  ${item.unit_price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                                </td>
                                <td className="px-4 py-3 text-right font-mono font-semibold text-slate-100">
                                  ${item.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot className="bg-slate-950/80 border-t border-slate-800 font-semibold text-slate-200">
                            <tr>
                              <td colSpan={4} className="px-4 py-2.5 text-right text-slate-400">
                                Tiền hàng (Subtotal):
                              </td>
                              <td className="px-4 py-2.5 text-right font-mono">
                                ${currentInvoice.subtotal.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                              </td>
                            </tr>
                            <tr>
                              <td colSpan={4} className="px-4 py-2.5 text-right text-slate-400">
                                Thuế (Tax):
                              </td>
                              <td className="px-4 py-2.5 text-right font-mono">
                                ${currentInvoice.tax_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                              </td>
                            </tr>
                            <tr className="border-t border-slate-800 text-sm">
                              <td colSpan={4} className="px-4 py-3 text-right font-bold text-white">
                                TỔNG CỘNG THANH TOÁN:
                              </td>
                              <td className="px-4 py-3 text-right font-bold font-mono text-emerald-400">
                                ${currentInvoice.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}{" "}
                                {currentInvoice.currency}
                              </td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6">
                      <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-emerald-400 font-mono text-xs overflow-x-auto max-h-[500px]">
                        {JSON.stringify({ invoice: currentInvoice, decision: currentDecision }, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: 20 HÓA ĐƠN MẪU (SAMPLES SHOWCASE) */}
        {activeTab === "samples" && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <span>Bộ 20 Hóa đơn mẫu thực nghiệm (Test Suite Matrix)</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  10 hóa đơn chuẩn doanh nghiệp + 10 hóa đơn thiết kế cố ý vi phạm từng rule kế toán để kiểm thử tự động.
                </p>
              </div>

              <div className="flex items-center space-x-3 w-full md:w-auto">
                <div className="relative flex-1 md:w-64">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Tìm kiếm theo mã lỗi, vendor..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {samples
                .filter(
                  (s) =>
                    s.filename.toLowerCase().includes(searchFilter.toLowerCase()) ||
                    s.vendor_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
                    s.notes.toLowerCase().includes(searchFilter.toLowerCase())
                )
                .map((sample, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-900/60 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 flex flex-col justify-between transition hover:-translate-y-0.5 hover:shadow-lg"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full border ${
                            sample.expected_outcome === "APPROVE"
                              ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                              : sample.expected_outcome === "REVIEW"
                              ? "bg-amber-950 text-amber-400 border-amber-800"
                              : "bg-rose-950 text-rose-400 border-rose-800"
                          }`}
                        >
                          {sample.expected_outcome}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400 font-bold">{sample.invoice_number}</span>
                      </div>

                      <h4 className="font-semibold text-sm text-slate-100">{sample.vendor_name}</h4>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">MST: {sample.tax_id}</p>
                      {sample.po_number && (
                        <p className="text-xs text-indigo-400 font-mono mt-0.5">PO: {sample.po_number}</p>
                      )}

                      <div className="my-2.5 p-2 bg-slate-950/70 rounded-lg border border-slate-800 text-[11px] text-slate-300">
                        <span className="text-slate-500 block mb-0.5">Mục đích kiểm thử:</span>
                        {sample.notes}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between mt-2">
                      <div>
                        <span className="text-[10px] text-slate-500 block">Số tiền</span>
                        <span className="text-xs font-bold font-mono text-slate-200">
                          ${sample.total.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                        </span>
                      </div>

                      <div className="flex items-center space-x-1.5">
                        <a
                          href={`${API_BASE}/api/samples/${sample.filename}/download`}
                          target="_blank"
                          rel="noreferrer"
                          title="Tải / Xem PDF gốc"
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>
                        <button
                          onClick={() => runSample(sample)}
                          className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1 shadow-sm shadow-indigo-600/30"
                        >
                          <span>Thẩm định</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* TAB 3: MASTER DATA */}
        {activeTab === "master-data" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Database className="w-5 h-5 text-indigo-400" />
                <span>Master Data Doanh nghiệp (Vendors & Purchase Orders)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Dữ liệu nguồn được dùng bởi Rule Engine để đối chiếu nhà cung cấp, kiểm tra trạng thái khóa (blocked), mã PO và hạn mức thanh toán.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Vendors Table */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-sky-400" />
                    <span>Danh sách Nhà cung cấp (10 Vendors)</span>
                  </h3>
                  <span className="text-xs text-slate-500">{vendors.length} nhà cung cấp</span>
                </div>

                <div className="divide-y divide-slate-800/60 max-h-[500px] overflow-y-auto">
                  {vendors.map((v) => (
                    <div key={v.id} className="p-4 hover:bg-slate-850/40 flex items-center justify-between text-xs">
                      <div className="space-y-0.5">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-indigo-400 font-bold">{v.id}</span>
                          <span className="font-semibold text-slate-200">{v.name}</span>
                          <span
                            className={`px-2 py-0.2 rounded-full text-[10px] font-bold uppercase border ${
                              v.status === "active"
                                ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                : "bg-rose-950 text-rose-400 border-rose-800"
                            }`}
                          >
                            {v.status}
                          </span>
                        </div>
                        <p className="text-slate-400 font-mono">MST: {v.tax_id}</p>
                      </div>

                      <div className="text-right">
                        <p className="text-slate-300 font-medium">Net {v.payment_terms_days} ngày</p>
                        <p className="text-[11px] text-slate-500">Hạn mức: ${v.credit_limit.toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Purchase Orders Table */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
                    <Receipt className="w-4 h-4 text-emerald-400" />
                    <span>Đơn đặt hàng phê duyệt (20 Purchase Orders)</span>
                  </h3>
                  <span className="text-xs text-slate-500">{pos.length} đơn PO</span>
                </div>

                <div className="divide-y divide-slate-800/60 max-h-[500px] overflow-y-auto">
                  {pos.map((p) => (
                    <div key={p.po_number} className="p-4 hover:bg-slate-850/40 flex items-center justify-between text-xs">
                      <div className="space-y-0.5">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-indigo-400 font-bold">{p.po_number}</span>
                          <span className="text-slate-400 font-mono">Vendor: {p.vendor_id}</span>
                          <span
                            className={`px-2 py-0.2 rounded-full text-[10px] font-bold uppercase border ${
                              p.status === "open"
                                ? "bg-sky-950 text-sky-400 border-sky-800"
                                : "bg-slate-800 text-slate-400 border-slate-700"
                            }`}
                          >
                            {p.status}
                          </span>
                        </div>
                        <p className="text-slate-500 truncate max-w-xs">
                          {p.lines && p.lines.length > 0 ? p.lines[0].item : "Dịch vụ đã phê duyệt"}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="text-sm font-bold font-mono text-slate-200">
                          ${p.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                        </p>
                        <p className="text-[10px] text-slate-500">Dung sai: +2%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: AUDIT LOG */}
        {activeTab === "history" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <History className="w-5 h-5 text-indigo-400" />
                <span>Nhật ký thẩm định & Phê duyệt hóa đơn (Audit Log)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Lưu trữ toàn bộ trace quyết định, thời điểm xử lý và các violation phát hiện để kiểm toán độc lập.
              </p>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">ID</th>
                    <th className="px-4 py-3">Số hóa đơn</th>
                    <th className="px-4 py-3">Nhà cung cấp</th>
                    <th className="px-4 py-3">PO</th>
                    <th className="px-4 py-3 text-right">Tổng tiền</th>
                    <th className="px-4 py-3 text-center">Quyết định</th>
                    <th className="px-4 py-3">Sai lệch (Violations)</th>
                    <th className="px-4 py-3 text-right">Thời gian</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {history.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3 font-mono text-slate-500">#{record.id}</td>
                      <td className="px-4 py-3 font-mono font-semibold text-slate-200">{record.invoice_number}</td>
                      <td className="px-4 py-3 text-slate-300">
                        {record.vendor_name}
                        <span className="block text-[10px] text-slate-500 font-mono">{record.tax_id}</span>
                      </td>
                      <td className="px-4 py-3 font-mono text-indigo-400">{record.po_number || "—"}</td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-slate-100">
                        ${record.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase border ${
                            record.outcome === "APPROVE"
                              ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                              : record.outcome === "REVIEW"
                              ? "bg-amber-950 text-amber-400 border-amber-800"
                              : "bg-rose-950 text-rose-400 border-rose-800"
                          }`}
                        >
                          {record.outcome}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">
                        {record.violations && record.violations.length > 0 ? (
                          <span className="text-rose-400 font-semibold font-mono">
                            {record.violations.map((v: any) => v.code).join(", ")}
                          </span>
                        ) : (
                          <span className="text-emerald-500 text-xs font-medium">Hợp lệ hoàn toàn</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-500 font-mono text-[11px]">
                        {new Date(record.processed_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={8} className="px-4 py-8 text-center text-slate-500">
                        Chưa có lượt thẩm định nào được lưu.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        <p>Hệ thống trích xuất & phê duyệt hóa đơn tự động · Phát triển theo chuẩn Enterprise Architecture</p>
      </footer>
    </div>
  );
}
