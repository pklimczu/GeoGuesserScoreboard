const headers = document.querySelectorAll('thead [scope=col]');
const headerParent = document.querySelector('thead tr');
const rows = document.querySelectorAll('tbody tr');
const table = [];
const wrongCols = [];

rows.forEach(row => {
  const tableRow = row.querySelectorAll('[scope=row]');
  table.push(tableRow);
});

for (let i = 0 ; i < headers.length;i++){
  console.log(`Checking ${headers[i].innerHTML} column...`);
  let isOk = false;
  for (let tableRow of table)
  {
    if (tableRow[i].innerHTML !== 'x')
    {
      isOk = true;
    }
  }
  if (isOk === false)
  {
    console.log(`User "${headers[i].innerHTML}" has no valid scores`);
    wrongCols.push(i);
  }
  else{
    console.log(`User "${headers[i].innerHTML}" has valid scores`);
  }
};

if (wrongCols.length !== 0)
{
  console.log('Removing headers:');
  for (let index of wrongCols)
  {
    console.log(`${headers[index].innerHTML}`);
    headerParent.removeChild(headers[index]);
  }

  console.log('Removing inner cells...');
  for (let i = 0 ; i < table.length; i++)
  {
    let tableRow = table[i];
    wrongCols.forEach((index)=>
    {
      rows[i].removeChild(tableRow[index]);
    });

  }

  console.log('DONE');
}
