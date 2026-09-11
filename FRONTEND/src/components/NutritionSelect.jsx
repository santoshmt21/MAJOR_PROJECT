import { useEffect, useRef, useState } from "react";

export default function NutritionSelect({ label, value, options, onChange, searchable = true }) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const selectRef = useRef(null);
  const filteredOptions = options.filter((option) => option.toLowerCase().includes(query.toLowerCase()));

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (!selectRef.current?.contains(event.target)) {
        setIsOpen(false);
        setQuery("");
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const chooseOption = (option) => {
    onChange(option);
    setIsOpen(false);
    setQuery("");
  };

  return (
    <div ref={selectRef} className="nutrition-combobox">
      <label className="nutrition-field-label">{label}</label>
      <button type="button" className={`nutrition-combobox-trigger ${isOpen ? "open" : ""}`} onClick={() => setIsOpen((open) => !open)} aria-haspopup="listbox" aria-expanded={isOpen}>
        <span>{value || "Select an option"}</span>
        <span className="nutrition-combobox-chevron">⌄</span>
      </button>
      {isOpen && (
        <div className="nutrition-combobox-menu" role="listbox">
          {searchable && <input autoFocus type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={`Search ${label.toLowerCase()}...`} className="nutrition-combobox-search" aria-label={`Search ${label}`} />}
          <div className="nutrition-combobox-options">
            {filteredOptions.length > 0 ? filteredOptions.map((option) => (
              <button type="button" role="option" aria-selected={option === value} className={`nutrition-combobox-option ${option === value ? "selected" : ""}`} key={option} onClick={() => chooseOption(option)}>
                <span>{option}</span>
                {option === value && <span>✓</span>}
              </button>
            )) : <div className="nutrition-combobox-empty">No matching options</div>}
          </div>
        </div>
      )}
    </div>
  );
}
