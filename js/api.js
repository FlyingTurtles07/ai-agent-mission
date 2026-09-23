async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(`API 오류 (${res.status}): ${errText}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  // 데이터 CRUD
  getDataList: () => apiRequest("/api/data"),
  createData: (payload) => apiRequest("/api/data", { method: "POST", body: JSON.stringify(payload) }),
  updateData: (id, payload) => apiRequest(`/api/data/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteData: (id) => apiRequest(`/api/data/${id}`, { method: "DELETE" }),

  // 대화 기록
  getConversations: () => apiRequest("/api/conversations"),
  getConversation: (id) => apiRequest(`/api/conversations/${id}`),
  deleteConversation: (id) => apiRequest(`/api/conversations/${id}`, { method: "DELETE" }),

  // 챗봇
  sendChat: (message, conversationId) => apiRequest("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId || null })
  })
};