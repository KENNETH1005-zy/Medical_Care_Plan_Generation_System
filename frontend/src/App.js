import React, { useEffect, useMemo, useRef, useState } from "react";

const apiBaseUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [patientInfo, setPatientInfo] = useState("");
  const [carePlanId, setCarePlanId] = useState(null);
  const [status, setStatus] = useState(null);
  const [carePlanText, setCarePlanText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const pollIntervalRef = useRef(null);

  const canSubmit = useMemo(() => patientInfo.trim().length > 0 && !isSubmitting, [
    patientInfo,
    isSubmitting,
  ]);

  const resetResult = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setCarePlanId(null);
    setStatus(null);
    setCarePlanText("");
    setErrorMessage("");
  };

  const handleGenerate = async () => {
    resetResult();
    setIsSubmitting(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/careplans/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patient_info: patientInfo }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || "Failed to start care plan generation.");
      }

      const data = await response.json();
      setCarePlanId(data.careplan_id);
      setStatus(data.status);
      setCarePlanText("");
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRefreshStatus = async (idOverride) => {
    const targetId = idOverride || carePlanId;
    if (!targetId) return;
    setErrorMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/api/careplan/${targetId}/status/`);
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || "Failed to fetch status.");
      }
      const data = await response.json();
      setStatus(data.status);

      if (data.status === "COMPLETED") {
        setCarePlanText(data.content || "");
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      } else if (data.status === "FAILED") {
        setErrorMessage("Care plan generation failed.");
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      }
    } catch (error) {
      setErrorMessage(error.message);
    }
  };

  useEffect(() => {
    if (!carePlanId) return;
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    handleRefreshStatus(carePlanId);
    pollIntervalRef.current = setInterval(() => {
      handleRefreshStatus(carePlanId);
    }, 3000);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [carePlanId]);

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif", maxWidth: "800px" }}>
      <h1>Care Plan MVP</h1>
      <p>输入患者信息，点击生成护理计划。</p>

      <textarea
        style={{ width: "100%", minHeight: "160px", marginBottom: "12px" }}
        placeholder="患者信息..."
        value={patientInfo}
        onChange={(event) => setPatientInfo(event.target.value)}
      />

      <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
        <button type="button" onClick={handleGenerate} disabled={!canSubmit}>
          {isSubmitting ? "生成中..." : "生成护理计划"}
        </button>
        <button type="button" onClick={() => handleRefreshStatus()} disabled={!carePlanId}>
          刷新状态
        </button>
      </div>

      {errorMessage && (
        <div style={{ color: "red", marginBottom: "12px" }}>{errorMessage}</div>
      )}

      {status && (
        <div style={{ marginBottom: "12px" }}>
          <strong>当前状态：</strong> {status}
        </div>
      )}

      {status === "COMPLETED" && carePlanText && (
        <div>
          <h2>护理计划</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f5f5f5", padding: "12px" }}>
            {carePlanText}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
