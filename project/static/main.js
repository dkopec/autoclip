// custom javascript

(function () {
  console.log('Sanity Check!');
})();

function handleClick(type) {
  fetch('/tasks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ type: type }),
  })
    .then(response => response.json())
    .then(data => {
      getStatus(data.task_id)
    })
}

function getStatus(taskID) {
  fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
    .then(response => response.json())
    .then(res => {
      console.log(res)
      var task_id = res.task_id
      var status_icon = '⚠️';
      switch (res.task_status) {
        case 'SUCCESS':
          status_icon = '✔️';
          break;
        case 'FAILURE':
          status_icon = '❌';
          break;
        case 'PENDING':
          status_icon = `<span class="emoji hourglass" role="img" aria-label="hourglass"></span>`;
          break;
      }
      var status = `${status_icon} ${res.task_status}`;
      var result = res.task_result;
      // Get a reference to the table and the rows of the table
      var table = document.getElementById("tasks");
      var rows = table.getElementsByTagName("tr");
      // Loop through the rows and check if a row with the specified id already exists
      var rowExists = false;
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var rowId = row.getAttribute("id");
        if (rowId == task_id) {
          // If a row with the specified id already exists, update the values of the cells in that row
          row.cells[1].innerHTML = status;
          row.cells[2].innerHTML = result;
          rowExists = true;
          break;
        }
      }
      // If a row with the specified id doesn't exist, create a new row and add it to the table
      if (!rowExists) {
        var newRow = document.createElement("tr");
        newRow.setAttribute("id", task_id);
        var id_cell = document.createElement("td");
        var status_cell = document.createElement("td");
        var result_cell = document.createElement("td");
        id_cell.innerHTML = task_id;
        status_cell.innerHTML = status;
        result_cell.innerHTML = result;
        newRow.appendChild(id_cell);
        newRow.appendChild(status_cell);
        newRow.appendChild(result_cell);
        table.appendChild(newRow);
      }
      const taskStatus = res.task_status;
      if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
      setTimeout(function () {
        getStatus(res.task_id);
      }, 5000);
    })
    .catch(err => console.log(err));
}

const form = document.getElementById('download-form');
const submitButton = document.getElementById('submit-button');
const taskIdElement = document.getElementById('task-id');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  var url = form.elements.url.value;
  fetch('/clip', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url: url }),
  })
  .then(response => response.json())
  .then(data => {
    getStatus(data.task_id)
  })
});
