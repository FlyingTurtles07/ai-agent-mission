const dataForm = document.getElementById("dataForm");
const dataTbody = document.getElementById("dataTbody");
const editId = document.getElementById("editId");
const fDate = document.getElementById("fDate");
const fValue = document.getElementById("fValue");
const fMemo = document.getElementById("fMemo");
const submitBtn = document.getElementById("submitBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");

async function loadDataTable() {
  const list = await api.getDataList();
  dataTbody.innerHTML = "";
  list.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.date}</td>
      <td>${item.value}</td>
      <td>${item.memo ?? ""}</td>
      <td>
        <button class="btn-ghost" data-edit="${item.id}">수정</button>
        <button class="btn-danger" data-del="${item.id}">삭제</button>
      </td>`;
    dataTbody.appendChild(tr);
  });
}

dataForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = { date: fDate.value, value: Number(fValue.value), memo: fMemo.value };
  try {
    if (editId.value) {
      await api.updateData(editId.value, payload);
    } else {
      await api.createData(payload);
    }
    resetForm();
    await loadDataTable();
  } catch (err) {
    alert("저장 실패: " + err.message);
  }
});

dataTbody.addEventListener("click", async (e) => {
  const editBtnId = e.target.getAttribute("data-edit");
  const delBtnId = e.target.getAttribute("data-del");

  if (editBtnId) {
    const row = e.target.closest("tr");
    const [date, value, memo] = row.querySelectorAll("td");
    editId.value = editBtnId;
    fDate.value = date.textContent;
    fValue.value = value.textContent;
    fMemo.value = memo.textContent;
    submitBtn.textContent = "수정 완료";
    cancelEditBtn.classList.remove("hidden");
  }

  if (delBtnId) {
    if (!confirm("삭제하시겠습니까?")) return;
    await api.deleteData(delBtnId);
    await loadDataTable();
  }
});

cancelEditBtn.addEventListener("click", resetForm);

function resetForm() {
  dataForm.reset();
  editId.value = "";
  submitBtn.textContent = "등록";
  cancelEditBtn.classList.add("hidden");
}

loadDataTable();