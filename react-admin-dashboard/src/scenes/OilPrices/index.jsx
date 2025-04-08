import { Box } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import { mockDataContacts } from "../../data/mockData";
import Header from "../../components/Header";
import { useTheme } from "@mui/material";
import { useEffect, useState } from "react";
import Papa from "papaparse";

const OilPrices = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [rows, setRows] = useState([]); 

  useEffect(() => {
    Papa.parse("/crude_oil_historical_data.csv", {
      header: true,
      download: true,
      complete: (results) => {
        const formattedResults = results.data.map((item, index) => ({
          id: index + 1, 
          date: item["Date"], 
          close: item["Close"], 
        })).filter(item => item.date && item.close); 
        setRows(formattedResults); 
      },
      error: (error) => {
        console.error("Error while parsing CSV:", error);
      },
    });
  }, []);
  

  const columns = [
    { field: "id", headerName: "ID", flex: 0.5 },
    { field: "date", headerName: "Date", flex:1 },
    {
      field: "close",
      headerName: "Close Price",
      type: "number",
      headerAlign: "left",
      align: "left",
      flex:1
    },
    
  ];

  return (
    <Box m="20px">
      <Header
        title="Historical Oil Prices"
        subtitle="Data from January 2021 to October 2024, taken from Yahoo! Finance API."
      />
      <Box
        m="40px 0 0 0"
        height="75vh"
        sx={{
          "& .MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-cell": {
            borderBottom: "none",
          },
          "& .name-column--cell": {
            color: colors.greenAccent[300],
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.blueAccent[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.blueAccent[700],
          },
          "& .MuiCheckbox-root": {
            color: `${colors.greenAccent[200]} !important`,
          },
          "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
            color: `${colors.grey[100]} !important`,
          },
        }}
      >
        <DataGrid
          rows={rows}
          columns={columns}
          components={{ Toolbar: GridToolbar }}
        />
      </Box>
    </Box>
  );
};

export default OilPrices;
