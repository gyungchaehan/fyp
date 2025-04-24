import { Box, Typography, useTheme, Link } from "@mui/material";
import { tokens } from "../theme";
import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';


const NewsBox = ({}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);


  const [rows, setRows] = useState([]);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch("https://newsapi.org/v2/everything?&q=Oil%20Price&pageSize=10");
        const data = await response.json();

        const tempRows = data.articles.map((article, index) => ({
          id: index, 
          source: article.source.name,
          title: article.title,
          publishedDate: article.publishedAt,
          articleUrl: article.url,
        }));

        setRows(tempRows);
      } catch (error) {
        console.error("Error fetching news:", error);
      }
    };

    fetchNews(); 
  }, []); 


  const columns = [
    { field: 'id', headerName: 'id', width: 50 },
    { field: 'source', headerName: 'Source', width: 100 },
    {
      field: 'title',
      headerName: 'Title',
      width: 150,
      editable: true,
      renderCell: (params) => (
        <Link href={params.row.articleUrl} target="_blank" rel="noopener noreferrer">
          {params.row.title}
        </Link>
      ),
    },
    {
      field: 'publishedDate',
      headerName: 'published At',
      width: 100,
      editable: true,
    },
  ];

  return (
    rows.map((row) => (
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        borderBottom={`4px solid ${colors.primary[500]}`}
        p="15px"
      >
        <Box>
          <Typography
            color={colors.greenAccent[500]}
            fontWeight="600"
          >
            {row.source}
          </Typography>
          <Link href={row.articleUrl} target="_blank" rel="noopener noreferrer">
            <Typography color={colors.grey[100]} style={{ textDecoration: 'underline' }}>
              {row.title}
            </Typography>
          </Link>
        </Box>
      </Box>
    ))
  );
};

export default NewsBox;
