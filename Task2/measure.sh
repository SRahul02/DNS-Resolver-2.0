#!/bin/bash

# --- Usage ---
# ./measure.sh <domain_list_file>
# Example: ./measure.sh h1_domains.txt

if [ -z "$1" ]; then
    echo "Usage: $0 <domain_list_file>"
    exit 1
fi

DOMAIN_FILE=$1
# Create a unique log file name, e.g., "h1_domains.txt" -> "h1_domains_baseline_report.log"
OUTPUT_LOG="${DOMAIN_FILE%.txt}_baseline_report.log"

SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_LATENCY=0

# Clear old log file and write header
echo "--- Starting Task B Baseline Measurement ---" > $OUTPUT_LOG
echo "Using Domain File: $DOMAIN_FILE" >> $OUTPUT_LOG
echo "------------------------------------------" >> $OUTPUT_LOG

while read -r domain; do
    if [ -z "$domain" ]; then continue; fi

    # Use 'dig' and get stats
    # +noall: Don't print the full answer
    # +stats: Print the final stats section (which includes Query time)
    OUTPUT=$(dig +stats "$domain")

    # Check if the resolution was successful (status: NOERROR)
    if echo "$OUTPUT" | grep -q "status: NOERROR"; then
        LATENCY_MS=$(echo "$OUTPUT" | grep "Query time:" | awk '{print $4}')

        # Handle cases where latency is 0 (cached locally by OS)
        if [ -z "$LATENCY_MS" ] || [ "$LATENCY_MS" -eq 0 ]; then
            LATENCY_MS=1 # Assume 1ms to avoid division by zero
        fi

        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        TOTAL_LATENCY=$((TOTAL_LATENCY + LATENCY_MS))
        echo "SUCCESS: $domain ($LATENCY_MS ms)" >> $OUTPUT_LOG
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "FAIL: $domain" >> $OUTPUT_LOG
    fi

sleep 0.5

done < "$DOMAIN_FILE"

# --- Final Report ---
# 'tee -a' prints to your screen AND appends to the log file
echo "-------------------------------------" | tee -a $OUTPUT_LOG
echo "Task B: Baseline Measurement Summary" | tee -a $OUTPUT_LOG
echo "-------------------------------------" | tee -a $OUTPUT_LOG
echo "Total Queries: $((SUCCESS_COUNT + FAIL_COUNT))" | tee -a $OUTPUT_LOG
echo "Successful Resolutions: $SUCCESS_COUNT" | tee -a $OUTPUT_LOG
echo "Failed Resolutions: $FAIL_COUNT" | tee -a $OUTPUT_LOG

if [ $SUCCESS_COUNT -gt 0 ]; then
    AVG_LATENCY=$(echo "scale=2; $TOTAL_LATENCY / $SUCCESS_COUNT" | bc)
    # Throughput as queries per second (1000ms / avg_latency_ms)
    AVG_THROUGHPUT=$(echo "scale=2; 1000 / $AVG_LATENCY" | bc)

    echo "Average Lookup Latency: ${AVG_LATENCY} ms" | tee -a $OUTPUT_LOG
    echo "Average Throughput: ${AVG_THROUGHPUT} queries/sec" | tee -a $OUTPUT_LOG
else
    echo "Average Lookup Latency: N/A" | tee -a $OUTPUT_LOG
    echo "Average Throughput: N/A" | tee -a $OUTPUT_LOG
fi