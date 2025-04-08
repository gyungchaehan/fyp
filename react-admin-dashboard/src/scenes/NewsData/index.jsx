import { Box, Typography, useTheme, Link } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import { useEffect, useState } from "react";
import Papa from "papaparse";

const NewsData = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [rows, setRows] = useState([]); 
  
    useEffect(() => {
      Papa.parse("/news_data_filtered.csv", {
        header: true,
        download: true,
        complete: (results) => {
          console.log(results)
          const formattedResults = results.data.map((item) => {
            const publishedAt = item['published_at'];
            const formattedPublishedAt = publishedAt 
            ? `${publishedAt.substring(0, 10)}, ${publishedAt.substring(11, 19)}` 
            : null; // or some default value

            return {
            id: item['id'], 
            title: item['title'],
            url: item['url'],
            published_at: formattedPublishedAt,
            source: item['source'] 
            };
          }).filter(item => item.id && item.title && item.url && item.published_at && item.source); 
          console.log(formattedResults);
          setRows(formattedResults); 
        },
        error: (error) => {
          console.error("Error while parsing CSV:", error);
        },
      });
    }, []);

  // ['id', 'title', 'url', 'published_at', 'source']
  const columns = [
    { field: "id", headerName: "ID" },
    {
      field: "title",
      headerName: "Title",
      flex: 1,
      editable: true,
      renderCell: (params) => (
        <Link href={params.row.url} target="_blank" rel="noopener noreferrer" className="title-column--cell">
          {params.row.title}
        </Link>
      ),
      cellClassName: 'title-column--cell'
    },
    {
      field: "published_at",
      headerName: "Published At",
      type: "date",
      headerAlign: "left",
      align: "left",
      flex: 1
    },
    {
      field: "source",
      headerName: "Source",
      flex: 1,
    },
  ];

  return (
    <Box m="20px">
      <Header title="News Data" subtitle="Data from January 2021 to October 2024, taken from The News API. Due to the large volume of data, only selected ones are displayed here." />
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
          "& .title-column--cell": {
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
        <DataGrid rows={rows} columns={columns} components={{ Toolbar: GridToolbar }}/>
      </Box>
    </Box>
  );
};

export default NewsData;
