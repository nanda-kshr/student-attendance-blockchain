// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Attendance {

    struct Record {
        string studentId;
        string date;
        string subjectCode;
        bool present;
    }

    Record[] public records;

    function getRecord(uint256 index)
        public
        view
        returns (
            string memory studentId,
            string memory date,
            string memory subjectCode,
            bool present
        )
    {
        Record storage record = records[index];
        return (record.studentId, record.date, record.subjectCode, record.present);
    }

    function markAttendance(
        string memory _studentId,
        string memory _date,
        string memory _subjectCode,
        bool _present
    ) public {

        records.push(
            Record(
                _studentId,
                _date,
                _subjectCode,
                _present
            )
        );
    }

    function getCount() public view returns(uint) {
        return records.length;
    }

    function getStudentRecordIndices(string memory studentId)
        public
        view
        returns (uint256[] memory)
    {
        uint256 total = records.length;
        uint256 count = 0;

        for (uint256 i = 0; i < total; i++) {
            if (_equals(records[i].studentId, studentId)) {
                count++;
            }
        }

        uint256[] memory indices = new uint256[](count);
        uint256 cursor = 0;
        for (uint256 i = 0; i < total; i++) {
            if (_equals(records[i].studentId, studentId)) {
                indices[cursor] = i;
                cursor++;
            }
        }

        return indices;
    }

    function _equals(string memory left, string memory right)
        internal
        pure
        returns (bool)
    {
        return keccak256(bytes(left)) == keccak256(bytes(right));
    }
}