import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const AttendanceModule = buildModule("AttendanceModule", (m) => {

  const attendance = m.contract("Attendance");

  return { attendance };
});

export default AttendanceModule;