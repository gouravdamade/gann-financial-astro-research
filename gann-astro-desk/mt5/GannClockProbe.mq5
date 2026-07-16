#property copyright "Gann Financial Astro Research"
#property link      "https://github.com/gouravdamade/gann-financial-astro-research"
#property version   "1.00"
#property service
#property strict

input string InpSymbol = "USDJPY";
input uint InpWriteIntervalMs = 2000;

const string PROBE_CONTRACT = "GANN_MT5_CLOCK_PROBE_V1";
const string PROBE_FILE = "gann_mt5_clock_probe_v1.csv";
const string TEMP_FILE = "gann_mt5_clock_probe_v1.tmp.csv";

bool WriteProbe(const ulong sequence)
  {
   MqlTick tick = {};
   if(!SymbolInfoTick(InpSymbol, tick))
     {
      PrintFormat("Clock probe could not read %s tick, error %d", InpSymbol, GetLastError());
      return false;
     }

   datetime h1_times[1];
   if(CopyTime(InpSymbol, PERIOD_H1, 0, 1, h1_times) != 1)
     {
      PrintFormat("Clock probe could not read %s H1 time, error %d", InpSymbol, GetLastError());
      return false;
     }

   datetime time_current = TimeCurrent();
   datetime time_trade_server = TimeTradeServer();
   datetime time_gmt = TimeGMT();
   datetime time_local = TimeLocal();
   int time_gmt_offset = TimeGMTOffset();
   int handle = FileOpen(
      TEMP_FILE,
      FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ,
      ',',
      CP_UTF8
   );
   if(handle == INVALID_HANDLE)
     {
      PrintFormat("Clock probe could not open temporary evidence file, error %d", GetLastError());
      return false;
     }

   FileWrite(
      handle,
      "contract",
      "probe_sequence",
      "written_at_gmt_epoch",
      "time_current_epoch",
      "time_trade_server_epoch",
      "time_gmt_epoch",
      "time_local_epoch",
      "time_gmt_offset_seconds",
      "tick_time_epoch",
      "tick_time_msc",
      "h1_bar_time_epoch",
      "terminal_build",
      "terminal_name",
      "terminal_company",
      "terminal_data_path",
      "terminal_common_data_path",
      "terminal_connected",
      "terminal_trade_allowed",
      "account_login",
      "account_server",
      "account_company",
      "account_trade_allowed",
      "account_trade_expert",
      "symbol",
      "bid",
      "ask",
      "period_seconds",
      "write_interval_ms"
   );
   FileWrite(
      handle,
      PROBE_CONTRACT,
      (long)sequence,
      (long)time_gmt,
      (long)time_current,
      (long)time_trade_server,
      (long)time_gmt,
      (long)time_local,
      time_gmt_offset,
      (long)tick.time,
      tick.time_msc,
      (long)h1_times[0],
      (int)TerminalInfoInteger(TERMINAL_BUILD),
      TerminalInfoString(TERMINAL_NAME),
      TerminalInfoString(TERMINAL_COMPANY),
      TerminalInfoString(TERMINAL_DATA_PATH),
      TerminalInfoString(TERMINAL_COMMONDATA_PATH),
      (int)TerminalInfoInteger(TERMINAL_CONNECTED),
      (int)TerminalInfoInteger(TERMINAL_TRADE_ALLOWED),
      (long)AccountInfoInteger(ACCOUNT_LOGIN),
      AccountInfoString(ACCOUNT_SERVER),
      AccountInfoString(ACCOUNT_COMPANY),
      (int)AccountInfoInteger(ACCOUNT_TRADE_ALLOWED),
      (int)AccountInfoInteger(ACCOUNT_TRADE_EXPERT),
      InpSymbol,
      DoubleToString(tick.bid, (int)SymbolInfoInteger(InpSymbol, SYMBOL_DIGITS)),
      DoubleToString(tick.ask, (int)SymbolInfoInteger(InpSymbol, SYMBOL_DIGITS)),
      PeriodSeconds(PERIOD_H1),
      (long)InpWriteIntervalMs
   );
   FileFlush(handle);
   FileClose(handle);

   ResetLastError();
   if(!FileMove(TEMP_FILE, FILE_COMMON, PROBE_FILE, FILE_COMMON | FILE_REWRITE))
     {
      PrintFormat("Clock probe could not publish evidence file, error %d", GetLastError());
      return false;
     }
   return true;
  }

int OnStart()
  {
   if(!SymbolSelect(InpSymbol, true))
     {
      PrintFormat("Clock probe could not select %s, error %d", InpSymbol, GetLastError());
      return 2;
     }
   uint interval = (uint)MathMax(1000, MathMin(60000, (int)InpWriteIntervalMs));
   ulong sequence = 0;
   PrintFormat("Read-only Gann clock probe started for %s", InpSymbol);
   while(!IsStopped())
     {
      sequence++;
      WriteProbe(sequence);
      Sleep(interval);
     }
   Print("Read-only Gann clock probe stopped");
   return 0;
  }
