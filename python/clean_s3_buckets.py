import argparse
import boto3
import datetime
import pytz


default_objs = set(["rubrik_cluster_lock.txt", "rubrik_encryption_key_check.txt"])


class S3Client(object):
    def __init__(self, profile):
        self._session = boto3.Session(profile_name=profile)
        self.s3 = self._session.resource("s3")

    def list_buckets(self, visitor):
        for b in self.s3.buckets.all():
            #print("processing bucket '{}'".format(b.name))

            # try:
            #     num = sum(1 for _ in b.objects.limit(3))
            #     if num == 0:
            #         print("failed to load objects for {}".format(b.name))
            # except Exception as ex:
            #     print("failed to load objects for {}: {}".format(b.name, ex))
            #     continue

            visitor(b)

    @staticmethod
    def delete_bucket(bucket):
        print("deleting {}".format(bucket.name))
        try:
            bucket.objects.all().delete()
        except Exception as ex:
            print("failed to delete objects {}".format(ex))
            return

        try:
            bucket.delete()
        except Exception as ex:
            print("failed to delete bucket {}".format(ex))
            return

    @staticmethod
    def is_bucket_too_old(bucket, days):
        num = sum(1 for _ in bucket.objects.limit(3))
        if num > 2:
            # has objects other than the default objects
            return False

        days_ago = pytz.UTC.localize(datetime.datetime.now()) - datetime.timedelta(days=days)
        for o in bucket.objects.all():
            if o.key not in default_objs:
                # has objects other than the default objects
                return False

            if o.last_modified > days_ago:
                # object has been modified recently
                return False

        if bucket.creation_date > days_ago:
            # buckets has been created recently
            return False

        return True

    @staticmethod
    def is_bucket_deletable(bucket, prefix, days):
        if prefix != "" and bucket.name.startswith(prefix):
            return S3Client.is_bucket_too_old(bucket, 5)

        return S3Client.is_bucket_too_old(bucket, days)

    @staticmethod
    def delete_bucket_if_necessary(bucket):
        if not S3Client.is_bucket_too_old(bucket, 21):
            return

        print("bucket {} will be deleted".format(bucket.name))
        S3Client.delete_bucket(bucket)


def parse_args():
    parser = argparse.ArgumentParser(description='cleanup the s3 buckets for AppFlows')
    parser.add_argument(
        '--profile', '-p',
        dest='profile',
        type=str,
        help='the name of the AWS profile')
    parser.add_argument(
        '--name', '-n',
        dest='prefix',
        type=str,
        default="",
        help='the prefix of the AWS s3 buckets to be check and removed')
    parser.add_argument(
        '--days', '-d',
        dest='days',
        type=str,
        help='the age of the AWS s3 buckets to be removed (days)')
    parser.add_argument(
        '--not-dry-run',
        dest='not_dry_run',
        action='store_true',
        help='delete the found buckets')
    return parser.parse_args()


def main():
    args = parse_args()
    names_to_be_deleted = []

    buckets_to_be_deleted = []

    def handle(bucket):
        print("\"{}\",".format(bucket.name))
        if "appflows-ui-" in bucket.name:
            buckets_to_be_deleted.append(bucket)
        if not S3Client.is_bucket_deletable(bucket, args.prefix, 5):
            return

        #print("found bucket {} to be deleted".format(bucket.name))
        #buckets_to_be_deleted.append(bucket)

    s3 = S3Client(args.profile)
    s3.list_buckets(handle)

    print("buckets to be deleted:")
    for b in buckets_to_be_deleted:
        print("\t{}".format(b.name))

    if args.not_dry_run:
        print("deleting buckets:")
        for b in buckets_to_be_deleted:
            S3Client.delete_bucket(b)


if __name__ == "__main__":
    main()
