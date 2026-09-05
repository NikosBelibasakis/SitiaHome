import { useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [message, setMessage] = useState("");
  const [isValid, setIsValid] = useState(null);
  const [loading, setLoading] = useState(false);

  const [executionTitle, setExecutionTitle] = useState("");
  const [executionDescription, setExecutionDescription] = useState("");

  const [recommendations, setRecommendations] = useState([]);

  async function handleSearch() {
    if (!prompt.trim()) {
      setIsValid(false);
      setMessage("Παρακαλώ περιγράψτε την κατοικία που αναζητάτε.");
      setExecutionTitle("");
      setExecutionDescription("");
      setRecommendations([]);
      return;
    }

    setLoading(true);
    setMessage("");
    setIsValid(null);
    setRecommendations([]);

    setExecutionTitle("ΕΛΕΓΧΟΣ ΑΙΤΗΜΑΤΟΣ");
    setExecutionDescription(
      "Ελέγχεται το αίτημα που έχετε καταχωρήσει ως προς την εγκυρότητά του."
    );

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(prompt),
      });

      const requirements = await response.json();

      if (requirements.legit_prompt) {
        setIsValid(true);
        setMessage("");

        setExecutionTitle("ΑΝΑΖΗΤΗΣΗ ΑΚΙΝΗΤΩΝ");
        setExecutionDescription(
          "Έγκυρο Αίτημα. Πραγματοποιείται αναζήτηση ακινήτων βάσει των προτιμήσεων και απαιτήσεών σας."
        );

        const propertiesResponse = await fetch(
          "http://127.0.0.1:8000/search-properties",
          {
            method: "POST",
          }
        );

        const propertiesFound = await propertiesResponse.json();

        if (propertiesFound) {
          setExecutionTitle("ΔΗΜΙΟΥΡΓΙΑ ΠΡΟΤΑΣΕΩΝ");
          setExecutionDescription(
            "Βρέθηκαν διαθέσιμες κατοικίες που πληρούν τις βασικές απαιτήσεις σας. Τώρα δημιουργούνται προτάσεις για την καλύτερη δυνατή επιλογή."
          );

          const selectedPropertiesResponse = await fetch(
  "http://127.0.0.1:8000/select-properties",
  {
    method: "POST",
  }
);

          const selectedProperties =
            await selectedPropertiesResponse.json();

          setRecommendations(selectedProperties);

          setExecutionTitle("ΔΗΜΙΟΥΡΓΗΘΗΚΑΝ ΤΕΛΙΚΕΣ ΠΡΟΤΑΣΕΙΣ");
          setExecutionDescription(
            "Έχουν δημιουργηθεί τελικές προτάσεις για τις κατοικίες που πληρούν όσο το δυνατόν περισσότερο τις απαιτήσεις σας."
          );
        } else {
          setExecutionTitle("ΔΕΝ ΒΡΕΘΗΚΑΝ ΑΚΙΝΗΤΑ");
          setExecutionDescription(
            "Δεν βρέθηκε κατοικία που να πληροί τις απαιτήσεις σας. Παρακαλώ υποβάλετε νέο αίτημα."
          );
        }
      } else {
        setIsValid(false);
        setMessage(requirements.validation_message);
        setExecutionTitle("");
        setExecutionDescription("");
         }
    } catch (error) {
      setIsValid(false);
      setMessage(
        "Παρουσιάστηκε πρόβλημα κατά την επικοινωνία με τον server."
      );

      setExecutionTitle("");
      setExecutionDescription("");
      setRecommendations([]);
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

        <div className="top-layout">

          <div className="search-column">

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
                    <strong>Υποχρεωτικά στοιχεία:</strong> μέγιστο ενοίκιο και ελάχιστος αριθμός υπνοδωματίων
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

            <section className="recommendations-section">

              <div className="recommendations-title">
                <span className="recommendations-icon">⌂</span>
                <h2>Προτεινόμενες Κατοικίες</h2>
              </div>

              <div className="recommendations-scroll">

                {recommendations.length === 0 ? (

                  <div className="recommendations-empty">
                    Οι προτεινόμενες κατοικίες θα εμφανιστούν εδώ μετά την
                    ολοκλήρωση της αναζήτησης.
                  </div>

                ) : (

                  <div className="recommendations-list">

                    {recommendations.map((item, index) => {
                      const property = item.property;

                      return (
                        <article
                          className="recommendation-card"
                          key={property.url}
                        >

                          <div className="recommendation-rank">
                            #{index + 1}
                          </div>

                          <div className="recommendation-content">

                            <div className="recommendation-header">

                              <h3>{property.title}</h3>

                              <span className="recommendation-price">
                                {property.price != null
                                  ? `${property.price} €`
                                  : "—"}
                              </span>

                            </div>

                            <div className="recommendation-info">

                              {property.location && (
                                <span>⌖ {property.location}</span>
                              )}

                              {property.area_sqm != null && (
                                <span>{property.area_sqm} τ.μ.</span>
                              )}

                              {property.bedrooms != null && (
                                <span>
                                  {property.bedrooms}{" "}
                                  {property.bedrooms === 1
                                    ? "υπνοδωμάτιο"
                                    : "υπνοδωμάτια"}
                                </span>
                              )}

                              <span>
                                {property.furnished
                                  ? "Επιπλωμένο"
                                  : "Μη επιπλωμένο"}
                              </span>

                            </div>

                            {property.description && (
                              <p className="recommendation-description">
                                {property.description}
                              </p>
                            )}

                            <div className="recommendation-opinion">
                              <span className="opinion-title">
                                Αξιολόγηση:
                              </span>

                              <span>
                                {item.opinion.opinion}
                              </span>
                            </div>

                            <a
                              className="recommendation-link"
                              href={property.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Προβολή αγγελίας ↗
                            </a>

                          </div>

                        </article>
                      );
                    })}

                  </div>

                )}

              </div>

            </section>

          </div>

          <section className="execution-section">

            <h2 className="execution-heading">
              ΚΑΤΑΣΤΑΣΗ ΕΚΤΕΛΕΣΗΣ
            </h2>

            {executionTitle && (
              <div className="execution-status">

                <div className="execution-title">
                  {executionTitle}
                </div>

                <div className="execution-description">
                  {executionDescription}
                </div>

              </div>
            )}

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;