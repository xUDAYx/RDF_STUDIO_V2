<!-- 
Online HTML, CSS and JavaScript editor to run code online.
-->
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <title>fiveVariableApp</title>
  <style>
    body {
     margin: 0;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    h1{
      margin:0px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    th, td {
      padding: 10px;      
      text-align: left;
      border: 1px dotted darkgray;
    }
    th {
      background-color: #f2f2f2;
    }

    .section {
      margin-top: 10px;
    }
    .section-header {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 10px;
    }
  </style>

  
</head>

<body>
  <div style="background-color:darkgray; margin:0px; padding:10px" >
    <!-- Button to toggle the border -->
    <input type="checkbox" id="myCheckbox" checked> Show Border
    <!-- Button to Decrease text size -->
    <button id="decreaseTextButton">Decrease Text Size</button>
    <!-- Button to Increase text size -->
    <button id="IncreaseTextButton">Increase Text Size</button>
    <hr>
  </div>

  <div class="container">

      <?php include "RDF_UI/fiveVariableAppUI.php"; ?>
   </div>


   <script type="text/javascript">


          // Get the table and button elements
        var table1 = document.getElementById("myTable");
        var IncreaseTextButton = document.getElementById("IncreaseTextButton");
        var decreaseTextButton = document.getElementById("decreaseTextButton");


        const checkbox = document.getElementById('myCheckbox');
        checkbox.addEventListener('change', function(){
          if (checkbox.checked) {
            //alert("Check Box Checked.......");
            setTableBorderForAlltheTables("1px dotted darkgray");
          }else {
            //alert("Check Box Checked");
            setTableBorderForAlltheTables("none");
          }
        });


        function setTableBorderForAlltheTables(borderStyle){
          // Get all table elements on the page
          var tables = document.querySelectorAll('table');
          // Loop through each table and apply the desired styles
          tables.forEach(function(table) {
              setTableBorder(table, borderStyle);
          });
        }

        
        function setTableBorder(table, borderStyle){
                 table.style.border = borderStyle; 
                // Get all the cells (both <th> and <td> elements)
                const cells = table.getElementsByTagName('td');
                const headers = table.getElementsByTagName('th');                
                // Combine cells and headers into a single array
                const allCells = Array.from(cells).concat(Array.from(headers));                
                // Loop through each cell and apply the desired style
                allCells.forEach(cell => {
                     cell.style.border = borderStyle;
                });
        }

       

        IncreaseTextButton.addEventListener("click", function () {
            // Call the function to Increase the text size
            IncreaseTextSize();
        });

        decreaseTextButton.addEventListener("click", function () {
            // Call the function to Increase the text size
            decreaseTextSize();
        });
    
    // Function to Increase the font size of all text elements in the page
        function IncreaseTextSize() {
            // Get all text-containing elements
            let elements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, td, a, b, i, u');
            // Iterate through all the elements and Increase their font size
            elements.forEach(element => {
                // Get the current font size
                let currentFontSize = window.getComputedStyle(element).fontSize;
                // Calculate the new font size
                let newFontSize = parseFloat(currentFontSize) * 1.1;
                // Update the element's font size
                element.style.fontSize = `${newFontSize}px`;
            });
        }

         // Function to Increase the font size of all text elements in the page
        function decreaseTextSize() {
            // Get all text-containing elements
            let elements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, td, a, b, i, u');
            // Iterate through all the elements and Increase their font size
            elements.forEach(element => {
                // Get the current font size
                let currentFontSize = window.getComputedStyle(element).fontSize;
                // Calculate the new font size
                let newFontSize = parseFloat(currentFontSize) * 0.9;
                // Update the element's font size
                element.style.fontSize = `${newFontSize}px`;
            });
        }

      

  </script>

</body>

</html>