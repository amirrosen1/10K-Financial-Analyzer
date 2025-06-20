// import React from "react";
// import {
//   Box,
//   Card,
//   CardContent,
//   Typography,
//   Table,
//   TableBody,
//   TableCell,
//   TableRow,
// } from "@mui/material";
//
// const Insights = ({ data }) => {
//   return (
//     <Box
//       sx={{
//         background: "linear-gradient(135deg, #f3f4f6, #e8eaf6)",
//         minHeight: "100vh",
//         display: "flex",
//         justifyContent: "center",
//         alignItems: "center",
//         padding: "20px",
//       }}
//     >
//       <Card
//         sx={{
//           maxWidth: "700px",
//           width: "100%",
//           borderRadius: "15px",
//           boxShadow: "0 8px 20px rgba(0,0,0,0.1)",
//         }}
//       >
//         <CardContent>
//           {/* Title */}
//           <Typography
//             variant="h4"
//             sx={{
//               textAlign: "center",
//               fontWeight: "bold",
//               marginBottom: "20px",
//               color: "#333",
//             }}
//           >
//             Document Insights
//           </Typography>
//
//           {/* Insights Table */}
//           <Table
//             sx={{
//               minWidth: "100%",
//               "& .MuiTableCell-root": {
//                 padding: "15px 20px",
//                 borderBottom: "1px solid rgba(0, 0, 0, 0.1)",
//               },
//             }}
//           >
//             <TableBody>
//               {data.map((item, index) => (
//                 <TableRow
//                   key={index}
//                   sx={{
//                     "&:hover": {
//                       backgroundColor: "#f5f5f5", // Subtle hover effect
//                     },
//                   }}
//                 >
//                   <TableCell
//                     sx={{
//                       fontWeight: "bold",
//                       color: "#555",
//                     }}
//                   >
//                     {item.label}
//                   </TableCell>
//                   <TableCell
//                     sx={{
//                       textAlign: "right",
//                       color: "#333",
//                     }}
//                   >
//                     {item.value}
//                   </TableCell>
//                 </TableRow>
//               ))}
//             </TableBody>
//           </Table>
//         </CardContent>
//       </Card>
//     </Box>
//   );
// };
//
// export default Insights;
