let currentConversationId = null;

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const convSelect = document.getElementById("convSelect");
const typingIndicator = document.getElementById("typingIndicator");
const newChatBtn = document.getElementById("newChatBtn");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user" : "ai"}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function loadConversationList() {
  try {
    const list = await api.getConversations();
    convSelect.innerHTML = `<option value="">+ 새 대화</option>`;
    list.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.title} (${c.message_count ?? 0}개 메시지)`;
      convSelect.appendChild(opt);
    });
  } catch (e) {
    console.error("대화 목록 로드 실패", e);
  }
}

async function loadConversationDetail(id) {
  chatMessages.innerHTML = "";
  if (!id) return;
  try {
    const detail = await api.getConversation(id);
    (detail.messages || []).forEach(m => addMessage(m.role === "user" ? "user" : "ai", m.content));
  } catch (e) {
    console.error("대화 상세 로드 실패", e);
  }
}

convSelect.addEventListener("change", async () => {
  currentConversationId = convSelect.value || null;
  await loadConversationDetail(currentConversationId);
});

newChatBtn.addEventListener("click", () => {
  currentConversationId = null;
  convSelect.value = "";
  chatMessages.innerHTML = "";
  chatInput.focus();
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chatInput.value = "";
  typingIndicator.classList.remove("hidden");

  try {
    const res = await api.sendChat(text, currentConversationId);
    typingIndicator.classList.add("hidden");
    addMessage("ai", res.reply);

    if (!currentConversationId && res.conversation_id) {
      currentConversationId = res.conversation_id;
      await loadConversationList();
      convSelect.value = currentConversationId;
    }
  } catch (err) {
    typingIndicator.classList.add("hidden");
    addMessage("ai", "⚠️ 오류가 발생했습니다: " + err.message);
  }
});

loadConversationList();