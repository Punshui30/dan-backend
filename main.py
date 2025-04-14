# === main.py PATCH ===

@app.get("/api/adapters/{adapter_id}/status")
def get_adapter_status(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        return {"adapter_id": adapter_id, "status": "not gated"}  # Fallback response
    return {"adapter_id": adapter_id, "status": adapter["status"]}


# === GateInManager.tsx PATCH ===

const execute = async (adapterId: string, action: string, params = {}) => {
  const adapter = state.adapters[adapterId];

  if (!adapter?.config?.base_url || !adapter?.config?.routes?.[action]) {
    showToast({
      title: "Missing Adapter Config",
      description: `Adapter \"${adapterId}\" is missing a base URL or route for \"${action}\".`,
      type: "error"
    });
    return;
  }

  try {
    const result = await executeAction(adapterId, action, params);
    return result.data?.message || "Action complete";
  } catch (err: any) {
    showToast({
      title: "Execution Error",
      description: err.message,
      type: "error"
    });
    return null;
  }
};


# === ToolDock.tsx PATCH ===

const handleRunAction = async (adapterId: string, action: string) => {
  const adapter = adapters[adapterId];
  if (!adapter?.config?.base_url || !adapter?.config?.routes?.[action]) {
    showToast({
      title: "Missing Config",
      description: `Adapter \"${adapterId}\" has no config or route defined for \"${action}\"`,
      type: "warning"
    });
    return;
  }

  try {
    await executeAction(adapterId, action);
    showToast({
      title: "Success",
      description: `Executed ${action} on ${adapterId}`,
      type: "success"
    });
  } catch (err: any) {
    showToast({
      title: "Execution Failed",
      description: err.message,
      type: "error"
    });
  }
};


# === useStatusPoller.ts (optional hook for live adapter sync) ===

import { useEffect } from "react";
import { getAdapterStatus } from "../lib/api";
import { useAdapters } from "../lib/AdaptersContext";

export function useStatusPoller(interval = 3000) {
  const { adapters, updateAdapter } = useAdapters();

  useEffect(() => {
    const poll = async () => {
      for (const adapterId in adapters) {
        try {
          const res = await getAdapterStatus(adapterId);
          updateAdapter({
            ...adapters[adapterId],
            status: res.status || "unknown"
          });
        } catch (e) {
          // ignore
        }
      }
    };

    const timer = setInterval(poll, interval);
    return () => clearInterval(timer);
  }, [adapters]);
}


# === Optional: Auto-Regate Adapter Memory on Refresh ===

// In AdaptersProvider useEffect
useEffect(() => {
  const raw = localStorage.getItem("dan_adapters");
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      setAdapters(parsed);
    } catch (e) {
      console.warn("Failed to parse adapters from storage");
    }
  }
}, []);
