export const BREEDS_INFO = [
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
    nutrition: { dm: "22–26 kg/day", protein: "16–18%", energy: "1.65–1.72 Mcal NEl/kg", fiber: "28–32% NDF", tips: "Requires high-energy TMR diet. Supplement with bypass protein during peak lactation. Ensure adequate calcium and phosphorus to prevent milk fever." }
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
    nutrition: { dm: "12–16 kg/day", protein: "12–14%", energy: "1.45–1.55 Mcal NEl/kg", fiber: "35–40% NDF", tips: "Thrives on crop residues and local fodder. Supplement with concentrates (1.5–2 kg) during lactation. Avoid high-grain diets to prevent acidosis." }
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
    nutrition: { dm: "14–18 kg/day", protein: "13–15%", energy: "1.50–1.62 Mcal NEl/kg", fiber: "32–36% NDF", tips: "Balance roughage with concentrates. Mineral supplementation critical — especially magnesium and phosphorus. Ensure salt licks year-round." }
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
    nutrition: { dm: "18–22 kg/day", protein: "11–13%", energy: "1.28–1.42 Mcal NEg/kg", fiber: "38–45% NDF", tips: "Finish on high-grain diet for 90–120 days for premium marbling. Avoid over-conditioning in breeding cows. Creep feeding calves improves weaning weights." }
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
    nutrition: { dm: "16–20 kg/day", protein: "17–19%", energy: "1.62–1.70 Mcal NEl/kg", fiber: "28–30% NDF", tips: "Higher metabolizable protein needed due to rich milk. Prone to hypocalcemia — pre-partum anion diet essential. Avoid overfeeding — obesity risk is high in Jerseys." }
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
    nutrition: { dm: "15–20 kg/day", protein: "10–12%", energy: "1.40–1.52 Mcal NEm/kg", fiber: "40–48% NDF", tips: "Maintains body condition on low-quality roughage. Supplement protein (urea-molasses block) in dry season. Provide shade and water during peak heat." }
  }
];

export const HERO_STATS = [
  { value: "50+", label: "Cattle Breeds" },
  { value: "85%", label: "AI Accuracy" },
  { value: "2s", label: "Avg. Predict Time" },
  { value: "10K+", label: "Farmers Helped" }
];
