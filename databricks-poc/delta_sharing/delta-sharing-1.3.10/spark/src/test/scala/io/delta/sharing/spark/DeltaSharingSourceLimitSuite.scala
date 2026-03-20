/*
 * Copyright (2021) The Delta Lake Project Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package io.delta.sharing.spark

import org.apache.spark.sql.{QueryTest}
import org.apache.spark.sql.streaming.{DataStreamReader, Trigger}
import org.apache.spark.sql.test.SharedSparkSession
import org.scalatest.time.SpanSugar._

class DeltaSharingSourceLimitSuite extends QueryTest
  with SharedSparkSession with DeltaSharingIntegrationTest {

  // VERSION 0: CREATE TABLE
  // VERSION 1: INSERT 3 rows, 3 add files
  // VERSION 2: REMOVE 1 row, 1 remove file
  // VERSION 3: UPDATE 1 row, 1 remove file and 1 add file
  lazy val tablePath = testProfileFile.getCanonicalPath + "#share8.default.cdf_table_cdf_enabled"

  val streamingTimeout = 30.seconds

  /**
   * Test maxFilesPerTrigger and maxBytesPerTrigger
   */
  def withStreamReaderAtVersion(startingVersion: String = "0"): DataStreamReader = {
    spark.readStream.format("deltaSharing").option("path", tablePath)
      .option("startingVersion", startingVersion)
      .option("ignoreDeletes", "true")
      .option("ignoreChanges", "true")
  }

  integrationTest("maxFilesPerTrigger - success with different values") {
    // Map from maxFilesPerTrigger to a list, the size of the list is the number of progresses of
    // the stream query, and each element in the list is the numInputRows for each progress.
    Map(1 -> Seq(1, 1, 1, 1), 2 -> Seq(2, 2), 3 -> Seq(3, 1), 4 -> Seq(4), 5 -> Seq(4)).foreach{
      case (k, v) =>
        val query = withStreamReaderAtVersion()
          .option("maxFilesPerTrigger", s"$k")
          .load().writeStream.format("console").start()

        try {
          query.processAllAvailable()
          val progress = query.recentProgress.filter(_.numInputRows != 0)
          assert(progress.length === v.size)
          progress.zipWithIndex.map { case (p, index) =>
            assert(p.numInputRows === v(index))
          }
        } finally {
          query.stop()
        }
    }
  }

  integrationTest("maxFilesPerTrigger - invalid parameter") {
    Seq("0", "-1", "string").foreach { invalidMaxFilesPerTrigger =>
      val message = intercept[IllegalArgumentException] {
        val query = withStreamReaderAtVersion()
          .option("maxFilesPerTrigger", invalidMaxFilesPerTrigger)
          .load().writeStream.format("console").start()
      }.getMessage
      for (msg <- Seq("Invalid", DeltaSharingOptions.MAX_FILES_PER_TRIGGER_OPTION, "positive")) {
        assert(message.contains(msg))
      }
    }
  }

  integrationTest("maxFilesPerTrigger - ignored when using Trigger.Once") {
    val query = withStreamReaderAtVersion()
      .option("maxFilesPerTrigger", "1")
      .load().writeStream.format("console")
      .trigger(Trigger.Once)
      .start()

    try {
      assert(query.awaitTermination(streamingTimeout.toMillis))
      val progress = query.recentProgress.filter(_.numInputRows != 0)
      assert(progress.length === 1) // only one trigger was run
      progress.foreach { p =>
        assert(p.numInputRows === 4)
      }
    } finally {
      query.stop()
    }
  }

  integrationTest("maxBytesPerTrigger - success with different values") {
    // Map from maxBytesPerTrigger to a list, the size of the list is the number of progresses of
    // the stream query, and each element in the list is the numInputRows for each progress.
    Map(1 -> Seq(1, 1, 1, 1), 1000 -> Seq(1, 1, 1, 1), 2000 -> Seq(2, 2),
      3000 -> Seq(3, 1), 4000 -> Seq(4), 5000 -> Seq(4)).foreach {
      case (k, v) =>
        val query = withStreamReaderAtVersion()
          .option("maxBytesPerTrigger", s"${k}b")
          .load().writeStream.format("console").start()

        try {
          query.processAllAvailable()
          val progress = query.recentProgress.filter(_.numInputRows != 0)
          assert(progress.length === v.size)
          progress.zipWithIndex.map { case (p, index) =>
            assert(p.numInputRows === v(index))
          }
        } finally {
          query.stop()
        }
    }
  }

  integrationTest("maxBytesPerTrigger - invalid parameter") {
    Seq("0", "-1", "string").foreach { invalidMaxFilesPerTrigger =>
      val message = intercept[IllegalArgumentException] {
        val query = withStreamReaderAtVersion()
          .option("maxBytesPerTrigger", invalidMaxFilesPerTrigger)
          .load().writeStream.format("console").start()
      }.getMessage
      for (msg <- Seq("Invalid", DeltaSharingOptions.MAX_BYTES_PER_TRIGGER_OPTION, "size")) {
        assert(message.contains(msg))
      }
    }
  }

  integrationTest("maxBytesPerTrigger - ignored when using Trigger.Once") {
    val query = withStreamReaderAtVersion()
      .option("maxBytesPerTrigger", "1b")
      .load().writeStream.format("console")
      .trigger(Trigger.Once)
      .start()

    try {
      assert(query.awaitTermination(streamingTimeout.toMillis))
      val progress = query.recentProgress.filter(_.numInputRows != 0)
      assert(progress.length === 1) // only one trigger was run
      progress.foreach { p =>
        assert(p.numInputRows === 4)
      }
    } finally {
      query.stop()
    }
  }

  integrationTest("maxBytesPerTrigger - max bytes and max files together") {
    // should process one file at a time
    val q = withStreamReaderAtVersion()
      .option(DeltaSharingOptions.MAX_FILES_PER_TRIGGER_OPTION, "1")
      .option(DeltaSharingOptions.MAX_BYTES_PER_TRIGGER_OPTION, "100gb")
      .load().writeStream.format("console").start()
    try {
      q.processAllAvailable()
      val progress = q.recentProgress.filter(_.numInputRows != 0)
      assert(progress.length === 4)
      progress.foreach { p =>
        assert(p.numInputRows === 1)
      }
    } finally {
      q.stop()
    }

    val q2 = withStreamReaderAtVersion()
      .option(DeltaSharingOptions.MAX_FILES_PER_TRIGGER_OPTION, "2")
      .option(DeltaSharingOptions.MAX_BYTES_PER_TRIGGER_OPTION, "1b")
      .load().writeStream.format("console").start()
    try {
      q2.processAllAvailable()
      val progress = q2.recentProgress.filter(_.numInputRows != 0)
      assert(progress.length === 4)
      progress.foreach { p =>
        assert(p.numInputRows === 1)
      }
    } finally {
      q2.stop()
    }
  }
}
