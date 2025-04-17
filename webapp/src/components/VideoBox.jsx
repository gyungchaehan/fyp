import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";
import { useEffect, useState } from 'react';

const VideoBox = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const [videoId, setVideoId] = useState('');
  const [videoSource, setVideoSource] = useState('');

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const response = await fetch("https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&order=relevance&q=Oil%2520price%2520news&relevanceLanguage=en&type=video&videoEmbeddable=true&key=AIzaSyD2uJTu9s8MyERPf5AXMC_9iSCPD-BhhOw");
        const data = await response.json();

        if (data.items && data.items.length > 0) {
          setVideoId(data.items[0].id.videoId);
          setVideoSource(data.items[0].snippet.channelTitle);
        } else {
          console.error("No video found");
        }
      } catch (error) {
        console.error("Error fetching video:", error);
      }
    };

    fetchVideo(); 
  }, []); 

  return (
    <Box justifyItems="center" width="100%">
      <iframe
        width="100%"
        height="100%"
        src={`https://www.youtube.com/embed/${videoId}`}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      ></iframe>
      <Typography
        variant="h5"
        sx={{ color: colors.greenAccent[600], marginBottom: 1 }}
        fontWeight="bold"
        fontStyle="italic"
        textAlign={"center"}
      >
        Source: <br />{videoSource}
      </Typography>
    </Box>
  );
};

export default VideoBox;