import { useState, useRef, useCallback, useEffect } from "react";
import backgroundImage from "./background.jpg";
import cowImage from "./cow.jpg";

const BREEDS_INFO = [
  {
    name: "Holstein",
    origin: "Netherlands",
    type: "Dairy",
    weight: "580–680 kg",
    lifespan: "20 years",
    milk: "7,000–10,000 L/year",
    color: "#2D5016",
    badge: "🥛 High Milk Yield",
    desc: "The world's highest-producing dairy cow, recognized by its distinctive black-and-white markings. Ideal for large-scale dairy farms with optimal feeding and management.",
    traits: ["High milk yield", "Adaptable", "Docile temperament", "Feed-efficient"],
    nutrition: {
      dm: "22–26 kg/day",
      protein: "16–18%",
      energy: "1.65–1.72 Mcal NEl/kg",
      fiber: "28–32% NDF",
      tips: "Requires high-energy TMR diet. Supplement with bypass protein during peak lactation. Ensure adequate calcium and phosphorus to prevent milk fever."
    }
  },
  {
    name: "Gir",
    origin: "Gujarat, India",
    type: "Dual Purpose",
    weight: "380–450 kg",
    lifespan: "25 years",
    milk: "1,200–3,500 L/year",
    color: "#8B4513",
    badge: "🌿 Indigenous Breed",
    desc: "One of India's premier indigenous breeds, prized for heat tolerance and disease resistance. The Gir produces A2 milk, known for its superior digestibility and nutritional profile.",
    traits: ["Heat tolerant", "Disease resistant", "A2 milk", "Low maintenance"],
    nutrition: {
      dm: "12–16 kg/day",
      protein: "12–14%",
      energy: "1.45–1.55 Mcal NEl/kg",
      fiber: "35–40% NDF",
      tips: "Thrives on crop residues and local fodder. Supplement with concentrates (1.5–2 kg) during lactation. Avoid high-grain diets to prevent acidosis."
    }
  },
  {
    name: "Sahiwal",
    origin: "Punjab, Pakistan/India",
    type: "Dairy",
    weight: "350–450 kg",
    lifespan: "22 years",
    milk: "2,000–4,000 L/year",
    color: "#C4872A",
    badge: "☀️ Tropical Breed",
    desc: "The best dairy breed among zebu cattle. Sahiwal is renowned for heat adaptation, tick resistance, and efficient milk production under tropical conditions.",
    traits: ["Tick resistant", "High butterfat", "Efficient converter", "Calm nature"],
    nutrition: {
      dm: "14–18 kg/day",
      protein: "13–15%",
      energy: "1.50–1.62 Mcal NEl/kg",
      fiber: "32–36% NDF",
      tips: "Balance roughage with concentrates. Mineral supplementation critical — especially magnesium and phosphorus. Ensure salt licks year-round."
    }
  },
  {
    name: "Angus",
    origin: "Scotland",
    type: "Beef",
    weight: "500–800 kg",
    lifespan: "20 years",
    milk: "Limited",
    color: "#1A1A1A",
    badge: "🥩 Premium Beef",
    desc: "World-renowned for exceptional marbling, tenderness, and beef quality. Naturally polled with a hardy constitution, making Angus a top choice for commercial beef producers globally.",
    traits: ["Superior marbling", "Naturally polled", "Hardy", "Early maturing"],
    nutrition: {
      dm: "18–22 kg/day",
      protein: "11–13%",
      energy: "1.28–1.42 Mcal NEg/kg",
      fiber: "38–45% NDF",
      tips: "Finish on high-grain diet for 90–120 days for premium marbling. Avoid over-conditioning in breeding cows. Creep feeding calves improves weaning weights."
    }
  },
  {
    name: "Jersey",
    origin: "Jersey Island",
    type: "Dairy",
    weight: "360–450 kg",
    lifespan: "20 years",
    milk: "4,500–6,500 L/year",
    color: "#C8A96E",
    badge: "🧈 Highest Butterfat",
    desc: "The Jersey's golden-tinged milk boasts the highest fat (5–6%) and protein content among major dairy breeds, making it perfect for artisan cheese and butter production.",
    traits: ["Rich butterfat", "Small frame", "Feed efficient", "Heat tolerant"],
    nutrition: {
      dm: "16–20 kg/day",
      protein: "17–19%",
      energy: "1.62–1.70 Mcal NEl/kg",
      fiber: "28–30% NDF",
      tips: "Higher metabolizable protein needed due to rich milk. Prone to hypocalcemia — pre-partum anion diet essential. Avoid overfeeding — obesity risk is high in Jerseys."
    }
  },
  {
    name: "Ongole",
    origin: "Andhra Pradesh, India",
    type: "Draft / Beef",
    weight: "450–650 kg",
    lifespan: "20 years",
    milk: "600–1,200 L/year",
    color: "#6B7280",
    badge: "💪 Draft Power",
    desc: "A magnificent white-grey Indian breed exported worldwide for crossbreeding. Ongole cattle are prized for drought resistance, superior draft ability, and quality beef production.",
    traits: ["Draft power", "Drought tolerant", "Large frame", "Disease hardy"],
    nutrition: {
      dm: "15–20 kg/day",
      protein: "10–12%",
      energy: "1.40–1.52 Mcal NEm/kg",
      fiber: "40–48% NDF",
      tips: "Maintains body condition on low-quality roughage. Supplement protein (urea-molasses block) in dry season. Provide shade and water during peak heat."
    }
  }
];

const HERO_STATS = [
  { value: "50+", label: "Cattle Breeds" },
  { value: "85%", label: "AI Accuracy" },
  { value: "2s", label: "Avg. Predict Time" },
  { value: "10K+", label: "Farmers Helped" }
];

export default function CattleCare() {
  const [activeTab, setActiveTab] = useState("identify");
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedBreed, setSelectedBreed] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [modelTab, setModelTab] = useState("vit");
  const [breedsList, setBreedsList] = useState(BREEDS_INFO);

  useEffect(() => {
    const fetchBreeds = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/breeds");
        if (res.ok) {
          const data = await res.json();
          if (data && data.length > 0) {
            setBreedsList(data);
          }
        }
      } catch (err) {
        console.error("Failed to fetch breeds from PostgreSQL database, falling back to static data:", err);
      }
    };
    fetchBreeds();
  }, []);

  // RAG Integration State
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState("idle"); // 'idle', 'loading', 'success', 'error'
  const [ingestError, setIngestError] = useState(null);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([
    {
      role: "assistant",
      content: "Welcome to the CattleCare AI Nutrition Advisor! Ask me any questions regarding cattle breeds and their nutrition routine."
    }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState(null);

  const fileRef = useRef();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (activeTab === "nutrition") {
      scrollToBottom();
    }
  }, [chatMessages, activeTab]);

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith("image/")) {
      setError("Please upload a valid image file (JPEG, PNG, WebP).");
      return;
    }
    setError(null);
    setResult(null);
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImage(url);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }, [handleFile]);

  const onDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = () => setIsDragging(false);

  const handlePredict = async () => {
    if (!imageFile) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    setModelTab("vit");
    try {
      const formData = new FormData();
      formData.append("file", imageFile);
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Prediction failed");
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not connect to backend. Make sure the server is running on port 8000.");
    } finally {
      setIsLoading(false);
    }
  };

  const clearImage = () => {
    setImage(null);
    setImageFile(null);
    setResult(null);
    setError(null);
    setSelectedBreed(null);
  };

  const triggerIngest = async () => {
    setIsIngesting(true);
    setIngestStatus("loading");
    setIngestError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/rag/ingest", {
        method: "POST"
      });
      if (!res.ok) {
        throw new Error("Failed to ingest documents");
      }
      const data = await res.json();
      if (data.status === "success") {
        setIngestStatus("success");
      } else {
        throw new Error(data.message || "Failed to ingest documents");
      }
    } catch (err) {
      setIngestStatus("error");
      setIngestError(err.message || "Could not connect to backend RAG service.");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSelectedBreed(null);
    if (tab === "nutrition") {
      triggerIngest();
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    const trimmed = chatInput.trim();
    if (!trimmed || isChatLoading) return;

    const userMsg = { role: "user", content: trimmed };
    setChatMessages(prev => [...prev, userMsg]);
    setChatInput("");
    setIsChatLoading(true);
    setChatError(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/rag/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: trimmed })
      });
      if (!res.ok) {
        throw new Error("Failed to get response from RAG service");
      }
      const data = await res.json();
      const botMsg = { role: "assistant", content: data.answer };
      setChatMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setChatError(err.message || "Error communicating with the RAG service.");
      const errorMsg = {
        role: "assistant",
        content: "⚠️ Sorry, I encountered an error while trying to fetch the answer. Make sure the backend server is running and the documents have been successfully ingested."
      };
      setChatMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const currentPrediction = result && modelTab === "yolo" ? result.yolo : result?.vit;
  const matchedBreed = currentPrediction
    ? breedsList.find(b => b.name.toLowerCase() === currentPrediction.predicted_class?.toLowerCase())
    : null;

  return (
    <div style={{
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      background: "#FAFAF7",
      minHeight: "100vh",
      color: "#1C1917",
      backgroundImage: `url(${backgroundImage})`,
      backgroundAttachment: "fixed",
      backgroundSize: "cover",
      backgroundPosition: "center",
      backgroundRepeat: "no-repeat",
      position: "relative"
    }}>
      {/* Semi-transparent overlay for readability */}
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(250, 250, 247, 0.85)",
        pointerEvents: "none",
        zIndex: 1
      }} />

      <div style={{ position: "relative", zIndex: 2 }}>
        <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root { --green: #1B4332; --amber: #D4831A; --cream: #FDF6EC; --wheat: #F5E6C8; --sage: #52796F; --light: #FAFAF7; }
        .nav-link { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.85); text-decoration: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; background: none; border: none; transition: background 0.2s, color 0.2s; }
        .nav-link:hover { background: rgba(255,255,255,0.12); color: #fff; }
        .nav-link.active { background: rgba(255,255,255,0.18); color: #fff; }
        .tab-btn { padding: 10px 24px; border: none; cursor: pointer; font-size: 14px; font-weight: 500; border-radius: 8px; transition: all 0.2s; background: transparent; color: #6B7280; }
        .tab-btn.active { background: #1B4332; color: #fff; }
        .tab-btn:hover:not(.active) { background: #F3F4F6; color: #1B4332; }
        .upload-zone { border: 2px dashed #C4B89A; border-radius: 16px; padding: 48px 24px; text-align: center; cursor: pointer; transition: all 0.2s; background: #FFFDF9; }
        .upload-zone.dragging { border-color: #D4831A; background: #FEF3E2; }
        .upload-zone:hover { border-color: #D4831A; background: #FEF9F0; }
        .btn-primary { background: #1B4332; color: #fff; border: none; padding: 14px 32px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s, transform 0.1s; display: inline-flex; align-items: center; gap: 8px; }
        .btn-primary:hover { background: #133226; }
        .btn-primary:active { transform: scale(0.98); }
        .btn-primary:disabled { background: #9CA3AF; cursor: not-allowed; }
        .btn-secondary { background: transparent; color: #1B4332; border: 1.5px solid #1B4332; padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
        .btn-secondary:hover { background: #1B4332; color: #fff; }
        .breed-card { background: #fff; border: 1px solid #E8E0D5; border-radius: 16px; padding: 24px; cursor: pointer; transition: all 0.2s; }
        .breed-card:hover { border-color: #D4831A; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(27,67,50,0.08); }
        .breed-card.selected { border-color: #1B4332; border-width: 2px; box-shadow: 0 8px 24px rgba(27,67,50,0.12); }
        .confidence-bar { height: 8px; border-radius: 4px; background: #E8E0D5; overflow: hidden; }
        .confidence-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #1B4332, #52796F); transition: width 1s ease; }
        .trait-pill { background: #EEF5EE; color: #1B4332; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; display: inline-block; }
        .stat-card { background: rgba(255,255,255,0.12); backdrop-filter: blur(4px); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; padding: 20px 24px; text-align: center; }
        .section-eyebrow { font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #D4831A; margin-bottom: 8px; }
        .nutrition-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #F3EDE3; }
        .nutrition-row:last-child { border-bottom: none; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .spinner { width: 24px; height: 24px; border: 3px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
        .fade-up { animation: fadeUp 0.4s ease forwards; }
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .hero-stats { grid-template-columns: repeat(2, 1fr) !important; }
          .breed-grid { grid-template-columns: 1fr !important; }
          .result-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>

        {/* ─── NAVBAR ─── */}
        <nav style={{ background: "#1B4332", position: "sticky", top: 0, zIndex: 100 }}>
          <div style={{ width: "100%", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: "#D4831A", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🐄</div>
              <div>
                <div style={{ fontFamily: "'Playfair Display', serif", color: "#fff", fontSize: 18, fontWeight: 700, lineHeight: 1.1 }}>CattleCare</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.55)", letterSpacing: "0.04em" }}>AI Breed Intelligence</div>
              </div>
            </div>

            <div className="desktop-nav" style={{ display: "flex", gap: 4 }}>
              {["identify", "breeds", "nutrition"].map(tab => (
                <button key={tab} className={`nav-link ${activeTab === tab ? "active" : ""}`}
                  onClick={() => handleTabChange(tab)}>
                  {tab === "identify" ? "🔍 Identify Breed" : tab === "breeds" ? "📚 Breed Library" : "🌾 Nutrition Guide"}
                </button>
              ))}
            </div>

            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              style={{ display: "none", background: "none", border: "none", color: "#fff", fontSize: 22, cursor: "pointer" }}
              className="mobile-menu-btn">☰</button>
          </div>
        </nav>

        {/* ─── HERO ─── */}
        <div style={{
          backgroundImage: `url(${cowImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          padding: "0",
          position: "relative",
          overflow: "hidden",
          width: "100%",
          minHeight: "500px"
        }}>
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.3)" }} />
          <div style={{ maxWidth: 800, margin: "0 auto", textAlign: "center", position: "relative", padding: "72px 24px 80px" }}>
            <div style={{ display: "inline-block", background: "rgba(212,131,26,0.2)", border: "1px solid rgba(212,131,26,0.4)", borderRadius: 20, padding: "4px 16px", marginBottom: 24 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "#FAC75A", letterSpacing: "0.08em", textTransform: "uppercase" }}>AI-Powered Cattle Intelligence</span>
            </div>
            <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(36px, 5vw, 60px)", fontWeight: 700, color: "#fff", lineHeight: 1.15, marginBottom: 20 }}>
              Know Your Herd.<br />
              <span style={{ color: "#FAC75A" }}>Grow Your Farm.</span>
            </h1>
            <p style={{ fontSize: "clamp(16px, 2vw, 20px)", color: "rgba(255,255,255,0.75)", lineHeight: 1.7, marginBottom: 16, maxWidth: 580, margin: "0 auto 16px" }}>
              Every animal tells a story. Every farmer deserves the tools to listen.
            </p>
            <p style={{ fontSize: 14, color: "rgba(255,255,255,0.5)", fontStyle: "italic", marginBottom: 48 }}>
              "Every herd counts. Every farmer matters."
            </p>
            <div className="hero-stats" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, maxWidth: 600, margin: "0 auto" }}>
              {HERO_STATS.map(s => (
                <div key={s.label} className="stat-card">
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#FAC75A", fontFamily: "'Playfair Display', serif" }}>{s.value}</div>
                  <div style={{ fontSize: 12, color: "rgba(255,255,255,0.65)", marginTop: 4 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ─── TAB BAR ─── */}
        <div style={{ background: "#fff", borderBottom: "1px solid #E8E0D5", position: "sticky", top: 64, zIndex: 90 }}>
          <div style={{ width: "100%", padding: "0 24px", display: "flex", gap: 8, overflowX: "auto" }}>
            {[
              { id: "identify", label: "🔍 Identify Breed", desc: "Upload & predict" },
              { id: "breeds", label: "📚 Breed Library", desc: "Explore breeds" },
              { id: "nutrition", label: "🌾 Nutrition Guide", desc: "Feeding tips" }
            ].map(t => (
              <button key={t.id} className={`tab-btn ${activeTab === t.id ? "active" : ""}`}
                onClick={() => handleTabChange(t.id)} style={{ whiteSpace: "nowrap" }}>
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* ─── CONTENT ─── */}
        <div style={{ width: "100%", padding: "48px 24px 80px" }}>

          {/* ════ TAB 1: IDENTIFY ════ */}
          {activeTab === "identify" && (
            <div className="fade-up">
              <div style={{ textAlign: "center", marginBottom: 48 }}>
                <div className="section-eyebrow">AI Breed Identification</div>
                <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: "#1B4332", marginBottom: 12 }}>Identify Any Cattle Breed</h2>
                <p style={{ color: "#6B7280", fontSize: 16, maxWidth: 520, margin: "0 auto" }}>
                  Upload a clear photo of your cattle. Our ViT model will identify the breed and provide tailored recommendations.
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40, alignItems: "start" }} className="result-grid">

                {/* Upload panel */}
                <div>
                  <div
                    className={`upload-zone ${isDragging ? "dragging" : ""}`}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    onDragLeave={onDragLeave}
                    onClick={() => !image && fileRef.current?.click()}
                  >
                    {image ? (
                      <div>
                        <img src={image} alt="Uploaded cattle" style={{ width: "100%", maxHeight: 320, objectFit: "cover", borderRadius: 12, marginBottom: 16 }} />
                        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
                          <button className="btn-primary" onClick={(e) => { e.stopPropagation(); handlePredict(); }} disabled={isLoading}
                            style={{ minWidth: 160 }}>
                            {isLoading ? <><div className="spinner" /> Analyzing...</> : <><span>🔍</span> Identify Breed</>}
                          </button>
                          <button className="btn-secondary" onClick={(e) => { e.stopPropagation(); clearImage(); }}>Clear</button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div style={{ fontSize: 56, marginBottom: 16 }}>🐄</div>
                        <p style={{ fontSize: 16, fontWeight: 600, color: "#374151", marginBottom: 8 }}>Drop your cattle photo here</p>
                        <p style={{ fontSize: 14, color: "#9CA3AF", marginBottom: 20 }}>or click to browse — JPEG, PNG, WebP accepted</p>
                        <button className="btn-primary" onClick={() => fileRef.current?.click()}>
                          📂 Choose Photo
                        </button>
                      </div>
                    )}
                  </div>
                  <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />

                  {/* Tips */}
                  <div style={{ background: "#F0F7F4", border: "1px solid #C3D9CF", borderRadius: 12, padding: 20, marginTop: 20 }}>
                    <p style={{ fontSize: 13, fontWeight: 600, color: "#1B4332", marginBottom: 10 }}>📸 Tips for best results</p>
                    {["Clear, well-lit side-profile photo", "Animal fills majority of the frame", "Avoid blurry or distant shots", "Single animal per photo works best"].map(tip => (
                      <div key={tip} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                        <span style={{ color: "#52796F", fontSize: 14 }}>✓</span>
                        <span style={{ fontSize: 13, color: "#4B5563" }}>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Results panel */}
                <div>
                  {error && (
                    <div style={{ background: "#FEF2F2", border: "1px solid #FCA5A5", borderRadius: 12, padding: 20, marginBottom: 20 }}>
                      <p style={{ color: "#B91C1C", fontSize: 14, fontWeight: 500 }}>⚠️ {error}</p>
                    </div>
                  )}

                  {!result && !error && (
                    <div style={{ background: "#fff", border: "1px solid #E8E0D5", borderRadius: 16, padding: 40, textAlign: "center", minHeight: 300, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                      <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.3 }}>🐾</div>
                      <p style={{ color: "#9CA3AF", fontSize: 15 }}>Upload an image to see breed identification results</p>
                    </div>
                  )}

                  {result && (
                    <div className="fade-up">
                      {/* Model Selection Tabs */}
                      <div style={{ display: "flex", gap: 8, marginBottom: 20, borderBottom: "1px solid #E8E0D5", paddingBottom: 12 }}>
                        <button
                          className={`tab-btn ${modelTab === "yolo" ? "active" : ""}`}
                          onClick={() => setModelTab("yolo")}
                          style={{ marginBottom: "-12px" }}
                        >
                          🔍 YOLO Model {result.yolo?.error ? "⚠️" : "✓"}
                        </button>
                        {result.vit && (
                          <button
                            className={`tab-btn ${modelTab === "vit" ? "active" : ""}`}
                            onClick={() => setModelTab("vit")}
                            style={{ marginBottom: "-12px" }}
                          >
                            🎨 ViT Model {result.vit?.error ? "⚠️" : "✓"}
                          </button>
                        )}
                      </div>

                      {/* Error State */}
                      {currentPrediction?.error && (
                        <div style={{ background: "#FEF2F2", border: "1px solid #FCA5A5", borderRadius: 12, padding: 20, marginBottom: 20 }}>
                          <p style={{ color: "#B91C1C", fontSize: 14, fontWeight: 500 }}>⚠️ {currentPrediction.error}</p>
                        </div>
                      )}

                      {/* Top prediction */}
                      {!currentPrediction?.error && currentPrediction && (
                        <>
                          <div style={{ background: "linear-gradient(135deg, #1B4332, #2D6A4F)", borderRadius: 16, padding: 28, marginBottom: 20, color: "#fff" }}>
                            <div style={{ fontSize: 12, fontWeight: 600, letterSpacing: "0.08em", color: "#86EFAC", textTransform: "uppercase", marginBottom: 8 }}>
                              Top Prediction {modelTab === "yolo" ? "- YOLO" : "- Vision Transformer"}
                            </div>
                            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 32, fontWeight: 700, marginBottom: 4 }}>{currentPrediction.predicted_class}</div>
                            <div style={{ fontSize: 14, color: "rgba(255,255,255,0.7)", marginBottom: 16 }}>{result.filename}</div>
                            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                              <div style={{ flex: 1 }}>
                                <div style={{ height: 8, borderRadius: 4, background: "rgba(255,255,255,0.2)", overflow: "hidden" }}>
                                  <div style={{ width: `${(currentPrediction.confidence * 100).toFixed(0)}%`, height: "100%", background: "#FAC75A", borderRadius: 4, transition: "width 1s ease" }} />
                                </div>
                              </div>
                              <div style={{ fontSize: 20, fontWeight: 700, color: "#FAC75A" }}>{(currentPrediction.confidence * 100).toFixed(1)}%</div>
                            </div>
                            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Confidence score</div>
                          </div>

                          {/* Top 5 */}
                          {currentPrediction.top5 && (
                            <div style={{ background: "#fff", border: "1px solid #E8E0D5", borderRadius: 16, padding: 24, marginBottom: 20 }}>
                              <p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 16 }}>Top 5 Predictions</p>
                              {currentPrediction.top5.map((item, i) => (
                                <div key={i} style={{ marginBottom: 12 }}>
                                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                                    <span style={{ fontSize: 13, color: i === 0 ? "#1B4332" : "#6B7280", fontWeight: i === 0 ? 600 : 400 }}>{item.class}</span>
                                    <span style={{ fontSize: 13, color: "#374151", fontWeight: 500 }}>{(item.confidence * 100).toFixed(1)}%</span>
                                  </div>
                                  <div className="confidence-bar">
                                    <div className="confidence-fill" style={{ width: `${(item.confidence * 100).toFixed(0)}%`, background: i === 0 ? "linear-gradient(90deg, #1B4332, #52796F)" : "#C4D9CC" }} />
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Matched breed info teaser */}
                          {matchedBreed && (
                            <div style={{ background: "#F0F7F4", border: "1px solid #C3D9CF", borderRadius: 12, padding: 20 }}>
                              <p style={{ fontSize: 13, fontWeight: 600, color: "#1B4332", marginBottom: 8 }}>Quick Breed Summary</p>
                              <p style={{ fontSize: 13, color: "#4B5563", lineHeight: 1.7, marginBottom: 12 }}>{matchedBreed.desc}</p>
                              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
                                {matchedBreed.traits.map(t => <span key={t} className="trait-pill">{t}</span>)}
                              </div>
                              <button className="btn-primary" style={{ fontSize: 13, padding: "10px 20px" }}
                                onClick={() => { setSelectedBreed(matchedBreed); }}>
                                View Full Breed Profile →
                              </button>
                            </div>
                          )}
                        </>
                      )}

                      {/* Comparison View */}
                      {result.yolo && result.vit && !result.yolo?.error && !result.vit?.error && (
                        <div style={{ background: "#FFFBF0", border: "2px solid #F5D89E", borderRadius: 16, padding: 24, marginTop: 24 }}>
                          <p style={{ fontSize: 13, fontWeight: 600, color: "#B45309", marginBottom: 16 }}>🔄 Model Comparison</p>
                          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                            <div style={{ background: "#fff", border: "1px solid #E8E0D5", borderRadius: 12, padding: 16 }}>
                              <div style={{ fontSize: 12, fontWeight: 600, color: "#6B7280", marginBottom: 8, textTransform: "uppercase" }}>YOLO Model</div>
                              <div style={{ fontSize: 18, fontWeight: 700, color: "#1B4332", marginBottom: 4 }}>{result.yolo.predicted_class}</div>
                              <div style={{ fontSize: 14, color: "#52796F", fontWeight: 600 }}>{(result.yolo.confidence * 100).toFixed(1)}%</div>
                            </div>
                            <div style={{ background: "#fff", border: "1px solid #E8E0D5", borderRadius: 12, padding: 16 }}>
                              <div style={{ fontSize: 12, fontWeight: 600, color: "#6B7280", marginBottom: 8, textTransform: "uppercase" }}>ViT Model</div>
                              <div style={{ fontSize: 18, fontWeight: 700, color: "#1B4332", marginBottom: 4 }}>{result.vit.predicted_class}</div>
                              <div style={{ fontSize: 14, color: "#52796F", fontWeight: 600 }}>{(result.vit.confidence * 100).toFixed(1)}%</div>
                            </div>
                          </div>
                          <div style={{ marginTop: 12, padding: 12, background: "#FEF3E2", borderRadius: 8 }}>
                            <p style={{ fontSize: 12, color: "#78350F" }}>
                              {result.yolo.predicted_class === result.vit.predicted_class
                                ? "✅ Both models agree on the breed prediction!"
                                : "⚠️ Models disagree - check confidence scores and consider the top prediction more carefully."}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Expanded breed detail on Identify page */}
              {selectedBreed && (
                <div className="fade-up" style={{ background: "#fff", border: "2px solid #1B4332", borderRadius: 20, padding: 40, marginTop: 32 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32, flexWrap: "wrap", gap: 16 }}>
                    <div>
                      <div className="section-eyebrow">Detailed Profile</div>
                      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 40, fontWeight: 700, color: "#1B4332" }}>{selectedBreed.name}</h2>
                      <p style={{ color: "#6B7280", marginTop: 6 }}>📍 Origin: {selectedBreed.origin} · Type: {selectedBreed.type}</p>
                    </div>
                    <button onClick={() => setSelectedBreed(null)} style={{ background: "#F3F4F6", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontSize: 13, color: "#374151" }}>✕ Close</button>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 }} className="result-grid">
                    <div>
                      <p style={{ fontSize: 15, color: "#4B5563", lineHeight: 1.75, marginBottom: 24 }}>{selectedBreed.desc}</p>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 12 }}>Key Characteristics</p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>
                        {selectedBreed.traits.map(t => (
                          <span key={t} style={{ background: "#F0F7F4", color: "#1B4332", border: "1px solid #C3D9CF", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 500 }}>{t}</span>
                        ))}
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        {[["⚖️ Average Weight", selectedBreed.weight], ["🕐 Lifespan", selectedBreed.lifespan], ["🥛 Milk Yield", selectedBreed.milk], ["🏷️ Breed Type", selectedBreed.type]].map(([k, v]) => (
                          <div key={k} style={{ background: "#F9F5EE", border: "1px solid #E8DED0", borderRadius: 10, padding: "14px 16px" }}>
                            <div style={{ fontSize: 12, color: "#9CA3AF", marginBottom: 4 }}>{k}</div>
                            <div style={{ fontSize: 15, fontWeight: 600, color: "#1B4332" }}>{v}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 16 }}>🌾 Nutrition Requirements</p>
                      <div style={{ background: "#FAFAF7", border: "1px solid #E8E0D5", borderRadius: 12, padding: 20, marginBottom: 20 }}>
                        {[["Dry Matter Intake", selectedBreed.nutrition.dm], ["Crude Protein", selectedBreed.nutrition.protein], ["Energy Density", selectedBreed.nutrition.energy], ["Fiber (NDF)", selectedBreed.nutrition.fiber]].map(([k, v]) => (
                          <div key={k} className="nutrition-row">
                            <span style={{ fontSize: 13, color: "#6B7280" }}>{k}</span>
                            <span style={{ fontSize: 14, fontWeight: 600, color: "#1B4332" }}>{v}</span>
                          </div>
                        ))}
                      </div>
                      <div style={{ background: "linear-gradient(135deg, #FEF3E2, #FFFDF9)", border: "1px solid #F5D89E", borderRadius: 12, padding: 20 }}>
                        <p style={{ fontSize: 12, fontWeight: 600, color: "#D4831A", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 10 }}>💡 Farmer's Tip</p>
                        <p style={{ fontSize: 13, color: "#78350F", lineHeight: 1.7 }}>{selectedBreed.nutrition.tips}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ════ TAB 2: BREED LIBRARY ════ */}
          {activeTab === "breeds" && (
            <div className="fade-up">
              <div style={{ textAlign: "center", marginBottom: 48 }}>
                <div className="section-eyebrow">Breed Encyclopedia</div>
                <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: "#1B4332", marginBottom: 12 }}>Cattle Breed Library</h2>
                <p style={{ color: "#6B7280", fontSize: 16, maxWidth: 500, margin: "0 auto" }}>Explore detailed profiles for common cattle breeds — from indigenous Indian breeds to global dairy & beef champions.</p>
              </div>

              <div className="breed-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24, marginBottom: 40 }}>
                {breedsList.map(breed => (
                  <div key={breed.name} className={`breed-card ${selectedBreed?.name === breed.name ? "selected" : ""}`}
                    onClick={() => setSelectedBreed(selectedBreed?.name === breed.name ? null : breed)}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                      <div style={{ width: 48, height: 48, borderRadius: 12, background: breed.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, flexShrink: 0 }}>🐄</div>
                      <span style={{ background: "#EEF5EE", color: "#1B4332", fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 20, border: "1px solid #C3D9CF" }}>{breed.badge}</span>
                    </div>
                    <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: "#1B4332", marginBottom: 4 }}>{breed.name}</h3>
                    <p style={{ fontSize: 12, color: "#9CA3AF", marginBottom: 12 }}>📍 {breed.origin} · {breed.type}</p>
                    <p style={{ fontSize: 13, color: "#6B7280", lineHeight: 1.6, marginBottom: 16 }}>{breed.desc.slice(0, 100)}...</p>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
                      {[["⚖️ Weight", breed.weight], ["🕐 Lifespan", breed.lifespan], ["🥛 Yield", breed.milk], ["🏷️ Type", breed.type]].map(([k, v]) => (
                        <div key={k} style={{ background: "#FAFAF7", borderRadius: 8, padding: "8px 12px" }}>
                          <div style={{ fontSize: 10, color: "#9CA3AF", marginBottom: 2 }}>{k}</div>
                          <div style={{ fontSize: 12, fontWeight: 600, color: "#374151" }}>{v}</div>
                        </div>
                      ))}
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                      {breed.traits.map(t => <span key={t} className="trait-pill">{t}</span>)}
                    </div>
                  </div>
                ))}
              </div>

              {/* Expanded breed detail */}
              {selectedBreed && (
                <div className="fade-up" style={{ background: "#fff", border: "2px solid #1B4332", borderRadius: 20, padding: 40, marginTop: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32, flexWrap: "wrap", gap: 16 }}>
                    <div>
                      <div className="section-eyebrow">Detailed Profile</div>
                      <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 40, fontWeight: 700, color: "#1B4332" }}>{selectedBreed.name}</h2>
                      <p style={{ color: "#6B7280", marginTop: 6 }}>📍 Origin: {selectedBreed.origin} · Type: {selectedBreed.type}</p>
                    </div>
                    <button onClick={() => setSelectedBreed(null)} style={{ background: "#F3F4F6", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontSize: 13, color: "#374151" }}>✕ Close</button>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 }} className="result-grid">
                    <div>
                      <p style={{ fontSize: 15, color: "#4B5563", lineHeight: 1.75, marginBottom: 24 }}>{selectedBreed.desc}</p>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 12 }}>Key Characteristics</p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>
                        {selectedBreed.traits.map(t => (
                          <span key={t} style={{ background: "#F0F7F4", color: "#1B4332", border: "1px solid #C3D9CF", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 500 }}>{t}</span>
                        ))}
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                        {[["⚖️ Average Weight", selectedBreed.weight], ["🕐 Lifespan", selectedBreed.lifespan], ["🥛 Milk Yield", selectedBreed.milk], ["🏷️ Breed Type", selectedBreed.type]].map(([k, v]) => (
                          <div key={k} style={{ background: "#F9F5EE", border: "1px solid #E8DED0", borderRadius: 10, padding: "14px 16px" }}>
                            <div style={{ fontSize: 12, color: "#9CA3AF", marginBottom: 4 }}>{k}</div>
                            <div style={{ fontSize: 15, fontWeight: 600, color: "#1B4332" }}>{v}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 16 }}>🌾 Nutrition Requirements</p>
                      <div style={{ background: "#FAFAF7", border: "1px solid #E8E0D5", borderRadius: 12, padding: 20, marginBottom: 20 }}>
                        {[["Dry Matter Intake", selectedBreed.nutrition.dm], ["Crude Protein", selectedBreed.nutrition.protein], ["Energy Density", selectedBreed.nutrition.energy], ["Fiber (NDF)", selectedBreed.nutrition.fiber]].map(([k, v]) => (
                          <div key={k} className="nutrition-row">
                            <span style={{ fontSize: 13, color: "#6B7280" }}>{k}</span>
                            <span style={{ fontSize: 14, fontWeight: 600, color: "#1B4332" }}>{v}</span>
                          </div>
                        ))}
                      </div>
                      <div style={{ background: "linear-gradient(135deg, #FEF3E2, #FFFDF9)", border: "1px solid #F5D89E", borderRadius: 12, padding: 20 }}>
                        <p style={{ fontSize: 12, fontWeight: 600, color: "#D4831A", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 10 }}>💡 Farmer's Tip</p>
                        <p style={{ fontSize: 13, color: "#78350F", lineHeight: 1.7 }}>{selectedBreed.nutrition.tips}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ════ TAB 3: NUTRITION ════ */}
          {activeTab === "nutrition" && (
            <div className="fade-up">
              <div style={{ textAlign: "center", marginBottom: 32 }}>
                <div className="section-eyebrow">Interactive Feeding Advisor</div>
                <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: "#1B4332", marginBottom: 12 }}>Cattle Care AI Advisor</h2>
                <p style={{ color: "#6B7280", fontSize: 16, maxWidth: 520, margin: "0 auto" }}>
                  Ask questions regarding cattle breeds, daily Dry Matter Intake, energy density, or custom nutrition routines.
                </p>
              </div>

              {/* Document Ingestion Status Banner */}
              <div style={{
                maxWidth: 850,
                margin: "0 auto 24px",
                background: ingestStatus === "loading" ? "#FEF3E2" : ingestStatus === "success" ? "#F0F7F4" : ingestStatus === "error" ? "#FEF2F2" : "#FFF",
                border: `1.5px solid ${ingestStatus === "loading" ? "#F5D89E" : ingestStatus === "success" ? "#C3D9CF" : ingestStatus === "error" ? "#FCA5A5" : "#E8E0D5"}`,
                borderRadius: 12,
                padding: "14px 20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
                boxShadow: "0 2px 10px rgba(0,0,0,0.01)"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 20 }}>
                    {ingestStatus === "loading" ? "⏳" : ingestStatus === "success" ? "✅" : ingestStatus === "error" ? "❌" : "📚"}
                  </span>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: ingestStatus === "success" ? "#1B4332" : ingestStatus === "error" ? "#B91C1C" : "#374151" }}>
                      {ingestStatus === "loading" && "Ingesting nutrition documents..."}
                      {ingestStatus === "success" && "Documents Ingested Successfully"}
                      {ingestStatus === "error" && "Document Ingestion Failed"}
                      {ingestStatus === "idle" && "Ready to ingest nutrition documents"}
                    </div>
                    <div style={{ fontSize: 12, color: "#6B7280", marginTop: 2 }}>
                      {ingestStatus === "loading" && "We are converting and indexing the PDF documents in the backend."}
                      {ingestStatus === "success" && "Vector store is ready. You can query breed-specific routines now."}
                      {ingestStatus === "error" && (ingestError || "Check if backend server is running and the Artifacts folder exists.")}
                      {ingestStatus === "idle" && "Click the button to manually trigger indexing."}
                    </div>
                  </div>
                </div>
                <button
                  className="btn-secondary"
                  onClick={triggerIngest}
                  disabled={isIngesting}
                  style={{
                    fontSize: 12,
                    padding: "6px 14px",
                    borderColor: ingestStatus === "success" ? "#C3D9CF" : "#1B4332",
                    color: ingestStatus === "success" ? "#52796F" : "#1B4332",
                    cursor: isIngesting ? "not-allowed" : "pointer"
                  }}
                >
                  {isIngesting ? "Ingesting..." : "Re-Ingest Data"}
                </button>
              </div>

              {/* Chat Container */}
              <div style={{
                maxWidth: 850,
                margin: "0 auto",
                background: "#fff",
                border: "1px solid #E8E0D5",
                borderRadius: 16,
                boxShadow: "0 8px 24px rgba(27,67,50,0.04)",
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                height: 550
              }}>
                {/* Chat Header */}
                <div style={{
                  background: "#1B4332",
                  padding: "16px 24px",
                  color: "#fff",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 10, height: 10, borderRadius: "50%", background: ingestStatus === "success" ? "#86EFAC" : "#FAC75A" }} />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 15 }}>RAG-Powered Nutrition Bot</div>
                      <div style={{ fontSize: 11, color: "rgba(255,255,255,0.7)" }}>Contextualized answers based on PDFs</div>
                    </div>
                  </div>
                  <button
                    onClick={() => setChatMessages([{
                      role: "assistant",
                      content: "Welcome to the CattleCare AI Nutrition Advisor! Ask me any questions regarding cattle breeds and their nutrition routine."
                    }])}
                    style={{
                      background: "none",
                      border: "none",
                      color: "rgba(255,255,255,0.8)",
                      fontSize: 12,
                      cursor: "pointer",
                      textDecoration: "underline"
                    }}
                  >
                    Clear Chat
                  </button>
                </div>

                {/* Chat Messages */}
                <div style={{
                  flex: 1,
                  padding: 24,
                  overflowY: "auto",
                  background: "#FAF9F6",
                  display: "flex",
                  flexDirection: "column",
                  gap: 16
                }}>
                  {chatMessages.map((msg, idx) => {
                    const isUser = msg.role === "user";
                    return (
                      <div
                        key={idx}
                        style={{
                          alignSelf: isUser ? "flex-end" : "flex-start",
                          maxWidth: "75%",
                          display: "flex",
                          flexDirection: "column",
                          alignItems: isUser ? "flex-end" : "flex-start"
                        }}
                      >
                        <div style={{
                          background: isUser ? "#1B4332" : "#FFF",
                          color: isUser ? "#FFF" : "#374151",
                          border: isUser ? "none" : "1px solid #E8E0D5",
                          borderRadius: isUser ? "16px 16px 2px 16px" : "16px 16px 16px 2px",
                          padding: "12px 18px",
                          fontSize: 14,
                          lineHeight: 1.5,
                          whiteSpace: "pre-wrap",
                          boxShadow: "0 2px 8px rgba(0,0,0,0.02)"
                        }}>
                          {msg.content}
                        </div>
                        <div style={{ fontSize: 10, color: "#9CA3AF", marginTop: 4, padding: "0 4px" }}>
                          {isUser ? "You" : "CattleCare Advisor"}
                        </div>
                      </div>
                    );
                  })}
                  {isChatLoading && (
                    <div style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{
                        background: "#FFF",
                        border: "1px solid #E8E0D5",
                        borderRadius: "16px 16px 16px 2px",
                        padding: "12px 18px",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.02)",
                        display: "flex",
                        alignItems: "center",
                        gap: 4
                      }}>
                        <div className="spinner" style={{ width: 14, height: 14, borderWidth: "2px", borderStyle: "solid", borderColor: "rgba(27,67,50,0.2)", borderTopColor: "#1B4332" }} />
                        <span style={{ fontSize: 13, color: "#6B7280" }}>Typing...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Suggestions row */}
                <div style={{
                  background: "#FFFDF9",
                  borderTop: "1px solid #F3EDE3",
                  padding: "10px 16px",
                  display: "flex",
                  gap: 8,
                  overflowX: "auto",
                  whiteSpace: "nowrap"
                }}>
                  {[
                    "Dry matter intake for Gir",
                    "Holstein milk yield nutrition tips",
                    "Universal guidelines for feeding dairy cattle",
                    "Mineral requirements for Sahiwal cow"
                  ].map((sug, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => {
                        if (!isChatLoading) {
                          setChatInput(sug);
                        }
                      }}
                      style={{
                        background: "#FFF",
                        border: "1px solid #E5DFD3",
                        borderRadius: 14,
                        padding: "6px 12px",
                        fontSize: 11,
                        color: "#52796F",
                        cursor: "pointer",
                        transition: "all 0.15s"
                      }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = "#1B4332"; e.currentTarget.style.color = "#1B4332"; }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = "#E5DFD3"; e.currentTarget.style.color = "#52796F"; }}
                    >
                      💡 {sug}
                    </button>
                  ))}
                </div>

                {/* Chat Input Form */}
                <form
                  onSubmit={handleSendMessage}
                  style={{
                    display: "flex",
                    borderTop: "1px solid #E8E0D5",
                    background: "#fff",
                    padding: 12,
                    gap: 10
                  }}
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    placeholder="Ask a question about breed characteristics or nutrition routines..."
                    disabled={isChatLoading}
                    style={{
                      flex: 1,
                      border: "1px solid #C4B89A",
                      borderRadius: 8,
                      padding: "10px 16px",
                      fontSize: 14,
                      outline: "none",
                      background: "#FFFDF9",
                      transition: "border-color 0.2s"
                    }}
                    onFocus={e => e.target.style.borderColor = "#1B4332"}
                    onBlur={e => e.target.style.borderColor = "#C4B89A"}
                  />
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={isChatLoading || !chatInput.trim()}
                    style={{
                      padding: "10px 24px",
                      borderRadius: 8,
                      fontSize: 14,
                      height: "100%"
                    }}
                  >
                    Send
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>

        {/* ─── FOOTER ─── */}
        <footer style={{ background: "#111827", color: "rgba(255,255,255,0.6)", padding: "40px 24px", width: "100%" }}>
          <div style={{ width: "100%", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 20 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <span style={{ fontSize: 20 }}>🐄</span>
                <span style={{ fontFamily: "'Playfair Display', serif", color: "#fff", fontSize: 18, fontWeight: 700 }}>CattleCare</span>
              </div>
              <p style={{ fontSize: 13, lineHeight: 1.6, maxWidth: 300 }}>AI-powered cattle breed intelligence for the modern farmer. Every herd counts. Every farmer matters.</p>
            </div>
            <div style={{ fontSize: 13 }}>
              <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, marginBottom: 4 }}>Powered by</p>
              <p style={{ color: "#86EFAC", fontWeight: 500 }}>ViT-Small/16 · Vision Transformer</p>
              <p style={{ fontSize: 12, marginTop: 4, color: "rgba(255,255,255,0.35)" }}>Backend: localhost:8000</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

