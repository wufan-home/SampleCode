template<class T>
class concurrent_queue{
public:
  void push( const T& data ){
    boost::mutex::scoped_lock l(m_mutex);
    m_queue.push(data);
    l.unlock();  

    // unlock first, then notify condition variable
    /*
      If the call to notify_one is still within the protected region, it is potentially sub-optimal: 
      the waiting thread might wake up immediately it is notified, and before the mutex is unlocked, in 
      which case it will have to block when the mutex is reacquired on the exit from wait. By rewriting 
      the function so that the notification comes after the mutex is unlocked, the waiting thread will 
      be able to acquire the mutex without blocking.
    */
    m_cond.notify_one();
  }

  T pop(){
    boost::mutex::scoped_lock l(m_mutex);
    m_cond.wait(l, []() { return m_queue.empty(); });
    T res = m_queue.front();

    //pop after we got the front element
    /*
      It is because if the resulting copy construction throws an exception, the element is lost: 
      it has been removed from the queue, and the caller has failed to obtain a copy. 
    */
    m_queue.pop();
    return res;
  }

  bool empty(){
    boost::mutex::scoped_lock l(m_mutex);
    return m_queue.empty();
  }

private:
  std::queue<T> m_queue;
  mutable boost::mutext m_mutex;
  boost::cond_variable m_cond;
};

// ===


//Assumption: std::queue has a member function full().
template<class T>
class concurrent_queue2{
public:
  void push( const T& data ){
      boost::mutex::scoped_lock l(m_mutex);
      while( m_queue.full() )
          m_cond_nonfull.wait(l);
      m_queue.push(data);
      l.unlock();
      m_cond_nonempty.notify_one();
  }

  T pop(){
      boost::mutex::scoped_lock l(m_mutex);
      while( m_queue.empty() )
          m_cond_nonempty.wait(l);
      T data = m_queue.front();
      m_queue.pop();
      l.unlock();
      m_cond_nonfull.notify_one();
  }

  bool empty(){
      boost::mutex::scoped_lock l(m_mutex);
      return m_queue.empty();
  }

  bool full(){
      boost::mutex::scoped_lock l(m_mutex);
      return m_queue.full();
  }

private:
  std::queue<T> m_queue;
  boost::mutex m_mutex;
  boost::cond_variable m_cond_nonfull;
  boost::cond_variable m_cond_nonempty;
};
