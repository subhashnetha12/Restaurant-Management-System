$(document).ready(function () {
  $('#form-data-table').DataTable({
    "pageLength": 10,
    "lengthMenu": [[10, 15, 20, 30, 50, -1], [10, 15, 20, 30, 50, "All"]]
  });
});
    

$('#AdminModal').on('hidden.bs.modal', function () {
  // Reset the form fields
  $('#AdminForm')[0].reset();
});  

$('#edit_AdminModal-{{ i.id }}').on('hidden.bs.modal', function () {
  // Reset the form fields
  $('#EditAdminForm-{{ i.id }}')[0].reset();
});