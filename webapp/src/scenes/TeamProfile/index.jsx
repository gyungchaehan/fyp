import React from "react";
import { Box, Typography, useTheme } from "@mui/material";
import leoImage from "./leo_fyp.JPG";
import adelImage from "./adel_cat.jpg";
import surlImage from "./surl_fyp.jpg";

const TeamProfile = () => {
  const theme = useTheme();

  const teamMembers = [
    {
      name: "Annika Kumar",
      role: "Team Member",
      description:
        "Annika is a year 4 CPEG major. She is interested in data science and software development.",
      image: leoImage,
    },
    {
      name: "Adelia Kusumawardhani",
      role: "Team Member",
      description:
        "Adel is a year 4 CS major. She is interested in finance and software development.",
      image: adelImage,
    },
    {
      name: "Gyungchae Han",
      role: "Team Member",
      description:
        "Gyungchae is a year 4 CS major. He is interested in cybersecurity and machine learning.",
      image: surlImage,
    },
  ];

  return (
    <Box
      sx={{
        backgroundColor: theme.palette.background.default,
        py: 5,
        px: 2,
      }}
    >
      <Typography
        variant="h4"
        align="center"
        sx={{
          fontWeight: "bold",
          mb: 4,
          color: theme.palette.text.primary,
        }}
      >
        Meet the Team
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr", // 1 column on small screens
            sm: "1fr 1fr", // 2 columns on medium screens
            lg: "1fr 1fr 1fr", // 3 columns on large screens
          },
          gap: 4,
        }}
      >
        {teamMembers.map((member, index) => (
          <Box
            key={index}
            sx={{
              backgroundColor: theme.palette.background.paper,
              borderRadius: 2,
              boxShadow: 3,
              p: 3,
              textAlign: "center",
            }}
          >
            <Box
              component="img"
              src={member.image}
              alt={member.name}
              sx={{
                width: 120,
                height: 120,
                borderRadius: "50%",
                objectFit: "cover",
                mb: 2,
              }}
            />
            <Typography
              variant="h6"
              sx={{ fontWeight: "bold", color: theme.palette.text.primary }}
            >
              {member.name}
            </Typography>
            <Typography
              variant="subtitle1"
              sx={{ color: theme.palette.text.secondary, mb: 1 }}
            >
              {member.role}
            </Typography>
            <Typography
              variant="body2"
              sx={{ color: theme.palette.text.secondary }}
            >
              {member.description}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default TeamProfile;
