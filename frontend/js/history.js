const historyList = document.getElementById("historyList");
const historyDetail = document.getElementById("historyDetail");
const detailTitle = document.getElementById("detailTitle");
const detailMessages = document.getElementById("detailMessages");
const closeDetailBtn = document.getElementById("closeDetailBtn");

async function loadHistoryList() {
  const list = await api.getConversations();
  historyList.innerHTML = "";
  list.forEach(c => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `<span>${c.title}</span><span>${c.message_count ?? 0}개 메시지 · ${c.created_at ?? ""}</span>`;
    div.addEventListener("click", () => openDetail(c.id));
    historyList.appendChild(div);
  });
}

async function openDetail(id) {
  const detail = await api.getConversation(id);
  detailTitle.textContent = detail.title;
  detailMessages.innerHTML = "";
  (detail.messages || []).forEach(m => {
    const div = document.createElement("div");
    div.className = `detail-msg ${m.role === "user" ? "user" : "assistant"}`;
    div.textContent = m.content;
    detailMessages.appendChild(div);
  });
  historyList.classList.add("hidden");
  historyDetail.classList.remove("hidden");
}

closeDetailBtn.addEventListener("click", () => {
  historyDetail.classList.add("hidden");
  historyList.classList.remove("hidden");
});

loadHistoryList();