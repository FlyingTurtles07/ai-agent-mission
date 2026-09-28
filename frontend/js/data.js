const dataForm = document.getElementById("dataForm");
const dataTbody = document.getElementById("dataTbody");
const editId = document.getElementById("editId");
const fDate = document.getElementById("fDate");
const fValue = document.getElementById("fValue");
const fMemo = document.getElementById("fMemo");
const submitBtn = document.getElementById("submitBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");
const summaryGrid = document.getElementById("summaryGrid");

// ---------- 요약 ----------
function flatten(obj, prefix = "") {
  const out = [];
  for (const [k, v] of Object.entries(obj || {})) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) out.push(...flatten(v, key));
    else out.push([key, Array.isArray(v) ? v.join(", ") : v]);
  }
  return out;
}

async function loadSummary() {
  try {
    const s = await api.getSummary();
    summaryGrid.innerHTML = "";
    flatten(s).forEach(([label, value]) => {
      const card = document.createElement("div");
      card.className = "summary-card";
      const l = document.createElement("div");
      l.className = "label";
      l.textContent = label;
      const v = document.createElement("div");
      v.className = "value";
      v.textContent = value;
      card.append(l, v);
      summaryGrid.appendChild(card);
    });
  } catch (e) {
    summaryGrid.textContent = "요약을 불러오지 못했습니다: " + e.message;
  }
}

// ---------- 그래프 ----------
let trendChart = null;
let statsCache = null;
const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

async function loadChart() {
  try {
    statsCache = await api.getStatistics();
    drawChart();
  } catch (e) {
    console.error("통계 로드 실패", e);
  }
}

function drawChart() {
  if (!statsCache) return;
  const series = statsCache.series || [];
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(document.getElementById("trendChart"), {
    type: "line",
    data: {
      labels: series.map((r) => r.date),
      datasets: [
        { label: "일별 신규계약", data: series.map((r) => r.value),
          borderColor: cssVar("--text-dim"), backgroundColor: "transparent",
          borderWidth: 1.5, pointRadius: 0, tension: 0.2 },
        { label: "7일 이동평균", data: series.map((r) => r.ma7),
          borderColor: cssVar("--accent"), backgroundColor: "transparent",
          borderWidth: 2.5, pointRadius: 0, tension: 0.3 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: cssVar("--text") } } },
      scales: {
        x: { ticks: { color: cssVar("--text-dim"), maxTicksLimit: 8 }, grid: { color: cssVar("--border") } },
        y: { ticks: { color: cssVar("--text-dim") }, grid: { color: cssVar("--border") } },
      },
    },
  });
}
window.addEventListener("themechange", drawChart);

// ---------- 목록 CRUD ----------
async function loadDataTable() {
  const list = await api.getDataList();
  dataTbody.innerHTML = "";
  list.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td></td><td></td><td></td>
      <td>
        <button class="btn-ghost" data-edit="${item.id}">수정</button>
        <button class="btn-danger" data-del="${item.id}">삭제</button>
      </td>`;
    const tds = tr.querySelectorAll("td");
    tds[0].textContent = item.date;
    tds[1].textContent = item.value;
    tds[2].textContent = item.memo ?? "";
    dataTbody.appendChild(tr);
  });
}

async function refreshAll() {
  await Promise.all([loadDataTable(), loadSummary(), loadChart()]);
}

dataForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = { date: fDate.value, value: Number(fValue.value), memo: fMemo.value };
  try {
    if (editId.value) await api.updateData(editId.value, payload);
    else await api.createData(payload);
    resetForm();
    await refreshAll();
  } catch (err) {
    alert("저장 실패: " + err.message);
  }
});

dataTbody.addEventListener("click", async (e) => {
  const editBtnId = e.target.getAttribute("data-edit");
  const delBtnId = e.target.getAttribute("data-del");

  if (editBtnId) {
    const [date, value, memo] = e.target.closest("tr").querySelectorAll("td");
    editId.value = editBtnId;
    fDate.value = date.textContent;
    fValue.value = value.textContent;
    fMemo.value = memo.textContent;
    submitBtn.textContent = "수정 완료";
    cancelEditBtn.classList.remove("hidden");
  }

  if (delBtnId) {
    if (!confirm("삭제하시겠습니까?")) return;
    try {
      await api.deleteData(delBtnId);
      await refreshAll();
    } catch (err) {
      alert("삭제 실패: " + err.message);
    }
  }
});

cancelEditBtn.addEventListener("click", resetForm);

function resetForm() {
  dataForm.reset();
  editId.value = "";
  submitBtn.textContent = "등록";
  cancelEditBtn.classList.add("hidden");
}

// ---------- JSON 내보내기 ----------
document.getElementById("exportBtn").addEventListener("click", async () => {
  try {
    const list = await api.getDataList();
    const blob = new Blob([JSON.stringify(list, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `data_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert("내보내기 실패: " + err.message);
  }
});

refreshAll();