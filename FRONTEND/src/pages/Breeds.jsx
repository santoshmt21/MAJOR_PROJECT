export default function Breeds({ breeds, selectedBreed, onSelectBreed, onCloseBreed }) {
  return (
    <div className="fade-up">
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <div className="section-eyebrow">Breed Encyclopedia</div>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: "#1B4332", marginBottom: 12 }}>Cattle Breed Library</h2>
        <p style={{ color: "#6B7280", fontSize: 16, maxWidth: 500, margin: "0 auto" }}>Explore detailed profiles for common cattle breeds — from indigenous Indian breeds to global dairy & beef champions.</p>
      </div>
      <div className="breed-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24, marginBottom: 40 }}>
        {breeds.map((breed) => (
          <div key={breed.name} className={`breed-card ${selectedBreed?.name === breed.name ? "selected" : ""}`} onClick={() => onSelectBreed(selectedBreed?.name === breed.name ? null : breed)}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: breed.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, flexShrink: 0 }}>🐄</div>
              <span style={{ background: "#EEF5EE", color: "#1B4332", fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 20, border: "1px solid #C3D9CF" }}>{breed.badge}</span>
            </div>
            <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: "#1B4332", marginBottom: 4 }}>{breed.name}</h3>
            <p style={{ fontSize: 12, color: "#9CA3AF", marginBottom: 12 }}>📍 {breed.origin} · {breed.type}</p>
            <p style={{ fontSize: 13, color: "#6B7280", lineHeight: 1.6, marginBottom: 16 }}>{breed.desc.slice(0, 100)}...</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
              {[['⚖️ Weight', breed.weight], ['🕐 Lifespan', breed.lifespan], ['🥛 Yield', breed.milk], ['🏷️ Type', breed.type]].map(([label, value]) => <div key={label} style={{ background: "#FAFAF7", borderRadius: 8, padding: "8px 12px" }}><div style={{ fontSize: 10, color: "#9CA3AF", marginBottom: 2 }}>{label}</div><div style={{ fontSize: 12, fontWeight: 600, color: "#374151" }}>{value}</div></div>)}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>{breed.traits.map((trait) => <span key={trait} className="trait-pill">{trait}</span>)}</div>
          </div>
        ))}
      </div>
      {selectedBreed && (
        <div className="fade-up" style={{ background: "#fff", border: "2px solid #1B4332", borderRadius: 20, padding: 40, marginTop: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32, flexWrap: "wrap", gap: 16 }}>
            <div><div className="section-eyebrow">Detailed Profile</div><h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 40, fontWeight: 700, color: "#1B4332" }}>{selectedBreed.name}</h2><p style={{ color: "#6B7280", marginTop: 6 }}>📍 Origin: {selectedBreed.origin} · Type: {selectedBreed.type}</p></div>
            <button onClick={onCloseBreed} style={{ background: "#F3F4F6", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontSize: 13, color: "#374151" }}>✕ Close</button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 }} className="result-grid">
            <div><p style={{ fontSize: 15, color: "#4B5563", lineHeight: 1.75, marginBottom: 24 }}>{selectedBreed.desc}</p><p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 12 }}>Key Characteristics</p><div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 24 }}>{selectedBreed.traits.map((trait) => <span key={trait} style={{ background: "#F0F7F4", color: "#1B4332", border: "1px solid #C3D9CF", padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 500 }}>{trait}</span>)}</div><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>{[['⚖️ Average Weight', selectedBreed.weight], ['🕐 Lifespan', selectedBreed.lifespan], ['🥛 Milk Yield', selectedBreed.milk], ['🏷️ Breed Type', selectedBreed.type]].map(([label, value]) => <div key={label} style={{ background: "#F9F5EE", border: "1px solid #E8DED0", borderRadius: 10, padding: "14px 16px" }}><div style={{ fontSize: 12, color: "#9CA3AF", marginBottom: 4 }}>{label}</div><div style={{ fontSize: 15, fontWeight: 600, color: "#1B4332" }}>{value}</div></div>)}</div></div>
            <div><p style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 16 }}>🌾 Nutrition Requirements</p><div style={{ background: "#FAFAF7", border: "1px solid #E8E0D5", borderRadius: 12, padding: 20, marginBottom: 20 }}>{[['Dry Matter Intake', selectedBreed.nutrition.dm], ['Crude Protein', selectedBreed.nutrition.protein], ['Energy Density', selectedBreed.nutrition.energy], ['Fiber (NDF)', selectedBreed.nutrition.fiber]].map(([label, value]) => <div key={label} className="nutrition-row"><span style={{ fontSize: 13, color: "#6B7280" }}>{label}</span><span style={{ fontSize: 14, fontWeight: 600, color: "#1B4332" }}>{value}</span></div>)}</div><div style={{ background: "linear-gradient(135deg, #FEF3E2, #FFFDF9)", border: "1px solid #F5D89E", borderRadius: 12, padding: 20 }}><p style={{ fontSize: 12, fontWeight: 600, color: "#D4831A", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 10 }}>💡 Farmer's Tip</p><p style={{ fontSize: 13, color: "#78350F", lineHeight: 1.7 }}>{selectedBreed.nutrition.tips}</p></div></div>
          </div>
        </div>
      )}
    </div>
  );
}
