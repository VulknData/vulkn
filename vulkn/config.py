# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


VulknConfig = {
    'metastore': '/home/kudos/vulkn/metastore',
    'tmp': 'vulkn_tmp'
}

VERSION_MAJOR = 19
VERSION_MINOR = 0
VERSION_PATCH = 7
VERSION_TEST = None
VERSION = '.'.join([str(VERSION_MAJOR), str(VERSION_MINOR), str(VERSION_PATCH)])

if VERSION_TEST:
    VERSION += '.' + VERSION_TEST

FLAGS = [
    'secure'
]

AUTH_OPTS = {
    'host': 'localhost',
    'port': 9000,
    'user': 'default',
    'password': None,
    'database': 'default'
}

EXTERNAL_FILE_OPTS = {
    'file': '-',
    'name': 'data',
    'format': 'TabSeparated',
    'structure': None,
    'types': None
}

SETTINGS = [
    'max_client_network_bandwidth',
    'server_logs_file',
    'min_compress_block_size',
    'max_compress_block_size',
    'max_block_size',
    'max_insert_block_size',
    'min_insert_block_size_rows',
    'min_insert_block_size_bytes',
    'max_threads',
    'max_read_buffer_size',
    'max_distributed_connections',
    'max_query_size',
    'interactive_delay',
    'connect_timeout',
    'connect_timeout_with_failover_ms',
    'receive_timeout',
    'send_timeout',
    'tcp_keep_alive_timeout',
    'queue_max_wait_ms',
    'poll_interval',
    'distributed_connections_pool_size',
    'connections_with_failover_max_tries',
    'use_uncompressed_cache',
    'replace_running_query',
    'background_pool_size',
    'background_schedule_pool_size',
    'distributed_directory_monitor_sleep_time_ms',
    'distributed_directory_monitor_batch_inserts',
    'optimize_move_to_prewhere',
    'replication_alter_partitions_sync',
    'replication_alter_columns_timeout',
    'load_balancing',
    'totals_mode',
    'totals_auto_threshold',
    'compile_expressions',
    'min_count_to_compile',
    'group_by_two_level_threshold',
    'group_by_two_level_threshold_bytes',
    'distributed_aggregation_memory_efficient',
    'aggregation_memory_efficient_merge_threads',
    'max_parallel_replicas',
    'parallel_replicas_count',
    'parallel_replica_offset',
    'skip_unavailable_shards',
    'distributed_group_by_no_merge',
    'merge_tree_min_rows_for_concurrent_read',
    'merge_tree_min_rows_for_seek',
    'merge_tree_coarse_index_granularity',
    'merge_tree_max_rows_to_use_cache',
    'merge_tree_uniform_read_distribution',
    'mysql_max_rows_to_insert',
    'optimize_min_equality_disjunction_chain_length',
    'min_bytes_to_use_direct_io',
    'force_index_by_date',
    'force_primary_key',
    'mark_cache_min_lifetime',
    'max_streams_to_max_threads_ratio',
    'network_compression_method',
    'network_zstd_compression_level',
    'log_queries',
    'log_queries_cut_to_length',
    'distributed_product_mode',
    'max_concurrent_queries_for_user',
    'insert_deduplicate',
    'insert_sample_with_metadata',
    'insert_quorum',
    'insert_quorum_timeout',
    'select_sequential_consistency',
    'table_function_remote_max_addresses',
    'read_backoff_min_latency_ms',
    'read_backoff_max_throughput',
    'read_backoff_min_interval_between_events_ms',
    'read_backoff_min_events',
    'memory_tracker_fault_probability',
    'enable_http_compression',
    'http_zlib_compression_level',
    'http_native_compression_disable_checksumming_on_decompress',
    'count_distinct_implementation',
    'output_format_write_statistics',
    'add_http_cors_header',
    'input_format_skip_unknown_fields',
    'input_format_import_nested_json',
    'input_format_values_interpret_expressions',
    'output_format_json_quote_64bit_integers',
    'output_format_json_quote_denormals',
    'output_format_json_escape_forward_slashes',
    'output_format_pretty_max_rows',
    'output_format_pretty_max_column_pad_width',
    'output_format_pretty_color',
    'use_client_time_zone',
    'send_progress_in_http_headers',
    'http_headers_progress_interval_ms',
    'fsync_metadata',
    'input_format_allow_errors_num',
    'input_format_allow_errors_ratio',
    'join_use_nulls',
    'join_default_strictness',
    'preferred_block_size_bytes',
    'max_replica_delay_for_distributed_queries',
    'fallback_to_stale_replicas_for_distributed_queries',
    'preferred_max_column_in_block_size_bytes',
    'insert_distributed_sync',
    'insert_distributed_timeout',
    'distributed_ddl_task_timeout',
    'stream_flush_interval_ms',
    'format_schema',
    'insert_allow_materialized_columns',
    'http_connection_timeout',
    'http_send_timeout',
    'http_receive_timeout',
    'optimize_throw_if_noop',
    'use_index_for_in_with_subqueries',
    'empty_result_for_aggregation_by_empty_set',
    'allow_distributed_ddl',
    'odbc_max_field_size',
    'max_rows_to_read',
    'max_bytes_to_read',
    'read_overflow_mode',
    'max_rows_to_group_by',
    'group_by_overflow_mode',
    'max_bytes_before_external_group_by',
    'max_rows_to_sort',
    'max_bytes_to_sort',
    'sort_overflow_mode',
    'max_bytes_before_external_sort',
    'max_bytes_before_remerge_sort',
    'max_result_rows',
    'max_result_bytes',
    'result_overflow_mode',
    'max_execution_time',
    'timeout_overflow_mode',
    'min_execution_speed',
    'timeout_before_checking_execution_speed',
    'max_columns_to_read',
    'max_temporary_columns',
    'max_temporary_non_const_columns',
    'max_subquery_depth',
    'max_pipeline_depth',
    'max_ast_depth',
    'max_ast_elements',
    'max_expanded_ast_elements',
    'max_rows_in_set',
    'max_bytes_in_set',
    'set_overflow_mode',
    'max_rows_in_join',
    'max_bytes_in_join',
    'join_overflow_mode',
    'max_rows_to_transfer',
    'max_bytes_to_transfer',
    'transfer_overflow_mode',
    'max_rows_in_distinct',
    'max_bytes_in_distinct',
    'distinct_overflow_mode',
    'max_memory_usage',
    'max_memory_usage_for_user',
    'max_memory_usage_for_all_queries',
    'max_network_bandwidth',
    'max_network_bytes',
    'max_network_bandwidth_for_user',
    'max_network_bandwidth_for_all_users',
    'format_csv_delimiter',
    'format_csv_allow_single_quotes',
    'format_csv_allow_double_quotes',
    'date_time_input_format',
    'log_profile_events',
    'log_query_settings',
    'log_query_threads',
    'send_logs_level',
    'enable_optimize_predicate_expression',
    'low_cardinality_max_dictionary_size',
    'low_cardinality_use_single_dictionary_for_part',
    'allow_experimental_low_cardinality_type',
    'decimal_check_overflow',
    'prefer_localhost_replica',
    'load_balancing',
    'max_fetch_partition_retries_count',
    'asterisk_left_columns_only',
    'http_max_multipart_form_data_size',
    'calculate_text_stack_trace',
    'allow_ddl',
    'parallel_view_processing',
    'enable_debug_queries',
    'low_cardinality_allow_in_native_format'
]
