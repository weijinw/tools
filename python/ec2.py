import boto3


class Ec2Client(object):
    def __init__(self, profile):
        self._session = boto3.Session(profile_name=profile)
        self.ec2 = self._session.resource("ec2")
        print('Profile {}, Region {}'.format(
            self._session.profile_name,
            self._session.region_name,
        ))

    def summary(self):
        count = 0
        for _ in self.ec2.instances.all():
            count += 1
        print("EC2 instances: {}".format(count))

        count = 0
        for _ in self.ec2.images.all():
            count += 1
        print("EC2 images: {}".format(count))

        count = 0
        for _ in self.ec2.snapshots.all():
            count += 1
        print("EC2 snapshots: {}".format(count))

    def list(self):
        print("Instances:")
        iter = self.ec2.instances.all()
        for i in iter:
            print('\t{}'.format(i['name']))

        print("Vpcs:")
        iter = self.ec2.vpcs.all()
        for i in iter:
            print('\t{}'.format(i.id))

        print("Images:")
        iter = self.ec2.images.all()
        for i in iter:
            print('\t{}'.format(i.id))

    # m0813
    # m0813
    # iam-location-1
    def delete_images(self):
        iter = self.ec2.images.page_size(count=100).filter(
            Filters=[
                # {
                #     'Name': 'tag:location_unique_id',
                #     'Values': [
                #         '*m0813*', '*alg0318*', '*iam-location-1*',
                #     ]
                # },
                {
                    'Name': 'tag:rk_source_vm_native_name',
                    'Values': [
                        '*appflows*',
                        '*wordpress*',
                        '*s-1373*',
                        '*s-1512*'
                    ]
                },
                # {
                #     'Name': 'tag:rk_version',
                #     'Values': [
                #         '*5.0.*',
                #     ]
                # },
            ],
        )
        for i in iter:
            tags = {}
            if i.tags:
                for t in i.tags:
                    tags[t['Key']] = t['Value']
            try:
                print("instance {} {}".format(i.id, tags['Name']))
                #i.delete()
                i.deregister()
            except Exception as e:
                print(e)

    def delete_snapshots(self):
        iter = self.ec2.snapshots.filter(
            Filters=[
                #  {
                #      'Name': 'tag:location_unique_id',
                #      'Values': [
                #          '*m0813*',
                #          '*m0730*',
                #          '*alg0318*',
                #          '*iam-location-1*',
                #          '*weijin*',
                #          '*april*',
                #          '*alg*',
                #          '*app0531*',
                #          '*appflows-ui*',
                #          '*yiyi*',
                #          '*rohit*'
                #      ]
                # },
                # {
                #     'Name': 'tag:rk_source_vm_native_name',
                #     'Values': [
                #         '*amanda*',
                #         '*april*',
                #         '*siyuan*',
                #         '*henry*',
                #         '*yuwei*',
                #         '*tz*',
                #         '*shaswat*',
                #     ]
                # },
                # {
                #     'Name': 'tag:rk_version',
                #     'Values': [
                #         '*5.0.*',
                #     ]
                # },
            ],
        )
        for i in iter:
            if "Created by CreateImage" not in i.description:
                continue
            if "781700226766" != i.owner_id:
                continue

            tags = {}
            if i.tags:
                for t in i.tags:
                    tags[t['Key']] = t['Value']
            print('\t{} {}'.format(i.id, tags.get('rk_object_name')))
            try:
                i.delete()
                print('{} deleted'.format(i.id))
            except Exception as e:
                print(e)


def main():
    client = Ec2Client("weijin-78")
    client.summary()


if __name__ == "__main__":
    main()
