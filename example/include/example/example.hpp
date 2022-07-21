#ifndef _EXAMPLE_H_
#define _EXAMPLE_H_

// TODO: -> annotations.h
#define SERIALIZABLE(type)
#define FIELD(type)

namespace ns1::ns2
{
	struct A
	{
		int a;
		float b;
	};
} // namespace ns1::ns2

namespace ns1
{
	namespace ns2
	{
		struct B
		{
			int a;
			float b;
		};
	} // namespace ns2
} // namespace ns1

SERIALIZABLE(ns1::ns2::A)
FIELD(ns1::ns2::A::a)
FIELD(ns1::ns2::A::b)

SERIALIZABLE(ns1::ns2::B)
FIELD(ns1::ns2::B::a)
FIELD(ns1::ns2::B::b)

#endif //_EXAMPLE_H_
