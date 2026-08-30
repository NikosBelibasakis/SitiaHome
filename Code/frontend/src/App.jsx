import { useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [message, setMessage] = useState("");
  const [isValid, setIsValid] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSearch() {
    if (!prompt.trim()) {
      setIsValid(false);
      setMessage("Παρακαλώ περιγράψτε την κατοικία που αναζητάτε.");
      return;
    }

    setLoading(true);
    setMessage("");
    setIsValid(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
        }),
      });

      const data = await response.json();

      if (data.legit_prompt) {
        setIsValid(true);
        setMessage(
          "Το αίτημα είναι έγκυρο. Η αναζήτηση μπορεί να προχωρήσει."
        );
      } else {
        setIsValid(false);
        setMessage(data.validation_message);
      }
    } catch (error) {
      setIsValid(false);
      setMessage("Παρουσιάστηκε πρόβλημα κατά την επικοινωνία με τον server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <span className="brand-sitia">Sitia</span>
          <span className="brand-home">Home</span>
        </div>

        <span className="subtitle">
          Εύρεση κατοικίας στον Δήμο Σητείας
        </span>
      </header>

      <main className="main-content">
        <section className="search-section">
          <div className="section-title">
            <span className="search-icon">⌕</span>
            <h2>Περιγραφή Αναζήτησης</h2>
          </div>

          <textarea
            className="search-textarea"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="π.χ. Ψάχνω κατοικία στη Σητεία με ενοίκιο 400€-600€, 2 δωμάτια, κοντά στο κέντρο..."
          />

          <div className="search-footer">
            <div className="requirements-info">
              <span className="info-icon">i</span>

              <span>
                <strong>Υποχρεωτικά στοιχεία:</strong> μέγιστο ενοίκιο, ελάχιστο ενοίκιο,
                αριθμός δωματίων
              </span>
            </div>

            <button
              className="search-button"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? "Επεξεργασία..." : "Αναζήτηση"}
            </button>
          </div>
        </section>

        {message && (
          <div
            className={`status-message ${
              isValid ? "status-success" : "status-error"
            }`}
          >
            <span className="status-icon">
              {isValid ? "✓" : "!"}
            </span>

            <span>{message}</span>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;