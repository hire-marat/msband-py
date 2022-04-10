import math
import pathlib
from msband.static.command import *
from msband.protocol import ProtocolInterface


# Connect using your preferred interface
iband : ProtocolInterface = ...


device_serial = iband.command(GetProductSerialNumber)
sync_folder = pathlib.Path('Sync').joinpath(device_serial)
sync_folder.mkdir(parents=True, exist_ok=True)


# Synchronise logs
remaining_logdata_chunks = iband.command(LoggerGetChunkCounts).LoggedChunkCount
for i in range(math.ceil(remaining_logdata_chunks/128.)):
    chunk_meta = iband.command(LoggerGetChunkRangeMetadata, ChunkCount=128)

    chunk_data = iband.command(
        LoggerGetChunkRangeData,
        StartingSeqNumber=chunk_meta.StartingSeqNumber,
        EndingSeqNumber=chunk_meta.EndingSeqNumber,
        DataLength=chunk_meta.ByteCount,
    )

    sync_folder.joinpath(
        f"{chunk_meta.StartingSeqNumber}-{chunk_meta.EndingSeqNumber}.log"
    ).write_bytes(chunk_data)

    iband.command(
        LoggerDeleteChunkRange,
        StartingSeqNumber=chunk_meta.StartingSeqNumber,
        EndingSeqNumber=chunk_meta.EndingSeqNumber,
        ByteCount=chunk_meta.ByteCount,
    )